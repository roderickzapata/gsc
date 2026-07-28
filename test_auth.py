from googleapiclient.discovery import build

from auth import authenticate
from models import Config

SITE_URL = "https://www.example.com/"


def main():
    config = Config(
        client_secrets_path="client_secret_1033492824682-7jj3k2q4f75c1t1gr0meb99r8kkttmct.apps.googleusercontent.com.json",
        token_store_path=".token_cache.json",
        site_url=SITE_URL,
    )

    print("Iniciando autenticación OAuth2...")
    creds = authenticate(config)
    print(f"Token válido: {creds.valid}")
    print(f"Token expirado: {creds.expired if hasattr(creds, 'expired') else 'N/A'}")

    print("\nConstruyendo cliente de Google Search Console...")
    service = build("searchconsole", "v1", credentials=creds)

    print(f"\nVerificando acceso a la propiedad: {SITE_URL}")
    try:
        result = service.sites().list().execute()
        sites = result.get("siteEntry", [])
        print(f"Sitios accesibles: {len(sites)}")
        for site in sites:
            print(f"  - {site.get('siteUrl')} (permiso: {site.get('permissionLevel')})")

        if any(s.get("siteUrl") == SITE_URL for s in sites):
            print(f"\n[OK] La propiedad {SITE_URL} es accesible.")
        else:
            print(f"\n[ERROR] La propiedad {SITE_URL} NO esta en la lista de sitios accesibles.")

    except Exception as e:
        print(f"Error al acceder a la API: {e}")


if __name__ == "__main__":
    main()
