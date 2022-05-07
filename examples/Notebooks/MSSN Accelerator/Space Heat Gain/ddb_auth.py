"""
   Authentication Service

    A service providing authentication for the DDB Python client

"""

import appdirs
import os
import msal
import atexit


class DDB_Exception(Exception):
    pass


class DDBAuth:
    def acquire_new_access_content(self, refreshToken=None):

        tenant = "4ae48b41-0137-4599-8661-fc641fe77bea"
        clientId = "817ad43f-c825-491f-9130-8cc4da1d4924"
        authority_url = "https://login.microsoftonline.com/" + tenant
        scopes = ["user.read", "api://ddb-api/user_impersonation"]

        # Cache implementation: https://msal-python.readthedocs.io/en/latest/index.html?highlight=PublicClientApplication#tokencache
        userDataDir = appdirs.user_data_dir("DDB", "Arup")
        token_cache = os.path.join(userDataDir, "TokenCachePy.msalcache.bin")

        if not os.path.exists(userDataDir):
            os.makedirs(userDataDir)

        result = None
        cache = msal.SerializableTokenCache()
        if os.path.exists(token_cache):
            cache.deserialize(open(token_cache, "r").read())

        def exit_func():
            if cache.has_state_changed:
                open(token_cache, "w").write(cache.serialize())

        atexit.register(exit_func)

        app = msal.PublicClientApplication(
            clientId, authority=authority_url, token_cache=cache
        )
        accounts = app.get_accounts()
        if accounts:
            # If so, you could then somehow display these accounts and let end user choose
            # Assuming the end user chose this one
            chosen = accounts[0]
            print("Using default account: " + chosen["username"])
            # Now let's try to find a token in cache for this account
            result = app.acquire_token_silent(scopes, account=chosen)

        if not result:
            # So no suitable token exists in cache. Let's get a new one from AAD.
            flow = app.initiate_device_flow(scopes=scopes)
            print(flow["message"])
            # Ideally you should wait here, in order to save some unnecessary polling
            # input("Press Enter after you successfully login from another device...")
            result = app.acquire_token_by_device_flow(flow)  # By default it will block

        if "access_token" not in result:
            print(result.get("error"))
            print(result.get("error_description"))
            # You may need this when reporting a bug
            print(result.get("correlation_id"))
            raise DDB_Exception("Authentication failure")

        # Force the cache to write in case we're in an emulator that doesn't exit (like juypter)
        exit_func()

        return result["access_token"]
