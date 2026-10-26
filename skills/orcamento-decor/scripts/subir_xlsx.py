# -*- coding: utf-8 -*-
"""Uploads a local .xlsx (decor budget) to a Drive folder as Raquel, through the Composio REST API.
  py -3 subir_xlsx.py --arquivo Orcamento_SPOT.xlsx --pasta <folder_id> [--sheets] [--user email]
Flow (same as conceito-interiores/scripts/subir_drive.py): Composio presigned PUT -> tools/execute
GOOGLEDRIVE_UPLOAD_FILE (<= 5 MB). --sheets also makes a Google Sheets copy (GOOGLEDRIVE_COPY_FILE_ADVANCED with
the Sheets mimeType) and prints its link. The key comes from COMPOSIO_API_KEY (via trocar-conta-google helper).
Prints one JSON line: {"xlsx_id", "sheet_id", "sheet_url"}.
"""
import argparse, hashlib, http.client, json, os, ssl, sys, urllib.error, urllib.parse, urllib.request
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                                "trocar-conta-google", "scripts"))
from composio_google import find_api_key, BASE

KEY = find_api_key()
XLSX = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
SHEET = "application/vnd.google-apps.spreadsheet"
LIMITE = 5 * 1024 * 1024  # Composio upload limit


def api(path, body, timeout=300):
    r = urllib.request.Request(BASE + path, data=json.dumps(body).encode(), method="POST")
    r.add_header("x-api-key", KEY)
    r.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(r, timeout=timeout) as resp:
        return json.loads(resp.read().decode())


def execute(user, slug, args):
    body = {"user_id": user, "arguments": args}
    try:
        res = api("/api/v3/tools/execute/" + slug, body)
    except urllib.error.HTTPError as e:
        if e.code != 404:
            raise
        body["version"] = "latest"  # some tools 404 without an explicit version
        res = api("/api/v3/tools/execute/" + slug, body)
    if not res.get("successful"):
        sys.exit("ERRO em %s: %s" % (slug, str(res.get("error"))[:800]))
    return res.get("data") or {}


def subir(user, caminho, pasta):
    dados = open(caminho, "rb").read()
    if len(dados) > LIMITE:
        sys.exit("ERRO: %s passa de 5 MB (limite do upload do Composio)" % caminho)
    nome = os.path.basename(caminho)
    md5 = hashlib.md5(dados).hexdigest()  # nosemgrep: integrity checksum required by the Composio upload API
    up = api("/api/v3/files/upload/request", {"toolkit_slug": "googledrive", "tool_slug": "GOOGLEDRIVE_UPLOAD_FILE",
                                              "filename": nome, "mimetype": XLSX, "md5": md5}, 120)
    u = urllib.parse.urlparse(up.get("new_presigned_url") or up.get("presigned_url"))
    conn = http.client.HTTPSConnection(u.netloc, timeout=600, context=ssl.create_default_context())
    conn.request("PUT", u.path + ("?" + u.query if u.query else ""), body=dados,
                 headers={"Content-Type": XLSX, "Content-Length": str(len(dados))})
    if conn.getresponse().status not in (200, 201, 204):
        sys.exit("ERRO: PUT do upload falhou")
    args = {"file_to_upload": {"name": nome, "s3key": up["key"], "mimetype": XLSX}}
    if pasta:
        args["folder_to_upload_to"] = pasta
    data = execute(user, "GOOGLEDRIVE_UPLOAD_FILE", args)
    return data.get("id") or (data.get("file") or {}).get("id")


def para_sheets(user, xlsx_id, nome, pasta):
    args = {"fileId": xlsx_id, "name": os.path.splitext(nome)[0], "mimeType": SHEET}
    if pasta:
        args["parents"] = [pasta]
    data = execute(user, "GOOGLEDRIVE_COPY_FILE_ADVANCED", args)
    return data.get("id") or (data.get("file") or {}).get("id")


def main():
    a = argparse.ArgumentParser()
    a.add_argument("--arquivo", required=True)
    a.add_argument("--pasta", default="", help="Drive folder id (empty = My Drive root)")
    a.add_argument("--sheets", action="store_true", help="also create a Google Sheets copy")
    a.add_argument("--user", default="raquel.tavares@seazone.com.br")
    o = a.parse_args()
    xlsx_id = subir(o.user, o.arquivo, o.pasta)
    out = {"xlsx_id": xlsx_id, "sheet_id": None, "sheet_url": None}
    if o.sheets and xlsx_id:
        sid = para_sheets(o.user, xlsx_id, os.path.basename(o.arquivo), o.pasta)
        out.update(sheet_id=sid, sheet_url="https://docs.google.com/spreadsheets/d/%s/edit" % sid if sid else None)
    print(json.dumps(out))


if __name__ == "__main__":
    main()
