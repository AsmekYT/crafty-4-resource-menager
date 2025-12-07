#everything above

SUBPAGE_PERMS = {
    #other perms
    "resource_manager": EnumPermissionsServer.FILES,
}

# paste bellow
#
#   async def async_read_config(self, file_path: Path):
#       async with aiofiles.open(file_path, "r") as file:
#           data = await file.read()
#       return data


    @tornado.web.authenticated
    async def post(self, page):
        api_key, token_data, exec_user = self.current_user
        superuser = exec_user["superuser"]
        if api_key is not None:
            superuser = superuser and api_key.full_access

        if superuser:
            exec_user_crafty_permissions = (
                self.controller.crafty_perms.list_defined_crafty_permissions()
            )
        else:
            if api_key is not None:
                exec_user_crafty_permissions = (
                    self.controller.crafty_perms.get_api_key_permissions_list(api_key)
                )
            else:
                exec_user_crafty_permissions = (
                    self.controller.crafty_perms.get_crafty_permissions_list(
                        exec_user["user_id"]
                    )
                )

        server_id = self.check_server_id()
        if not server_id:
            return

        subpage = self.get_argument("subpage", "")

        if subpage == "resource_manager":
            action = self.get_argument("action", "")

            if action == "install":
                project_id = self.get_argument("project_id")
                resource_type = self.get_argument("resource_type", "mod")
                game_version = self.get_argument("game_version", "")
                loader = self.get_argument("loader", "")

                q_backup = self.get_argument("q_backup", "")

                try:
                    versions_url = f"https://api.modrinth.com/v2/project/{project_id}/version"

                    params = {}
                    if game_version:
                        params["game_versions"] = json.dumps([game_version])
                    if loader:
                        params["loaders"] = json.dumps([loader])

                    async with httpx.AsyncClient() as client:
                        ver_response = await client.get(versions_url, params=params)
                        ver_response.raise_for_status()
                        versions = ver_response.json()

                        if not versions:
                            self.redirect(
                                f"/panel/server_detail?id={server_id}&subpage=resource_manager&q={q_backup}&error=NoCompatibleVersionFound")
                            return

                        target_file = versions[0]['files'][0]
                        download_url = target_file['url']
                        filename = target_file['filename']

                        server_data = self.controller.servers.get_server_data_by_id(server_id)
                        server_path = server_data['path']

                        target_dir = "mods"
                        if resource_type == "plugin":
                            target_dir = "plugins"
                        elif resource_type == "shader":
                            target_dir = "shaderpacks"
                        elif resource_type == "resourcepack":
                            target_dir = "resourcepacks"

                        save_dir = os.path.join(server_path, target_dir)
                        os.makedirs(save_dir, exist_ok=True)
                        save_path = os.path.join(save_dir, filename)

                        logger.info(f"Resource Manager: Downloading {filename} to {save_path}")

                        async with client.stream("GET", download_url) as response:
                            response.raise_for_status()
                            async with aiofiles.open(save_path, "wb") as f:
                                async for chunk in response.aiter_bytes():
                                    await f.write(chunk)

                        self.redirect(
                            f"/panel/server_detail?id={server_id}&subpage=resource_manager&q={q_backup}&status=success")
                        return

                except Exception as e:
                    logger.error(f"Resource Manager Install Failed: {e}")
                    self.redirect(
                        f"/panel/server_detail?id={server_id}&subpage=resource_manager&q={q_backup}&error=InstallFailed")
                    return

        self.redirect(f"/panel/dashboard")


# inside get keep everything and add as bellow shown

    @tornado.web.authenticated
    async def get(self, page):

# inside elif page == "server_detail":
#
#           if subpage == "webhooks":
#               page_data["webhooks"] = (
#                   self.controller.management.get_webhooks_by_server(
#                       server_id, model=True
#                   )
#               )
#               page_data["triggers"] = list(
#                   WebhookFactory.get_monitored_events().keys()
#               )
# add this:

            if subpage == "resource_manager":
                server_data = self.controller.servers.get_server_data_by_id(server_id)
                server_path = server_data.get("path")

                detected_type = "plugin"

                if os.path.isdir(os.path.join(server_path, "plugins")):
                    detected_type = "plugin"
                elif os.path.isdir(os.path.join(server_path, "mods")):
                    detected_type = "mod"

                search_query = self.get_argument("q", default="")
                resource_type = self.get_argument("type", default=detected_type)
                loader_filter = self.get_argument("loader", default="")

                server_version = page_data.get("server_stats", {}).get("version", "")
                clean_version = ""

                if server_version and str(server_version) != "False" and server_version != "N/A":
                    clean_version = str(server_version).split(" ")[0]

                user_version = self.get_argument("version", default=clean_version)

                modrinth_results = []
                error_message = None

                if search_query:
                    try:
                        facets = []

                        if resource_type:
                            facets.append([f"project_type:{resource_type}"])

                        if user_version:
                            facets.append([f"versions:{user_version}"])

                        if loader_filter:
                            facets.append([f"categories:{loader_filter}"])

                        modrinth_api_url = "https://api.modrinth.com/v2/search"
                        params = {
                            "query": search_query,
                            "limit": 20,
                            "index": "relevance",
                            "facets": json.dumps(facets)
                        }

                        api_token = self.helper.get_setting("modrinth_api_token")
                        headers = {
                            "User-Agent": "CraftyController/Resource-Manager"
                        }
                        if api_token:
                            headers["Authorization"] = api_token

                        async with httpx.AsyncClient() as client:
                            response = await client.get(modrinth_api_url, params=params, headers=headers)

                            if response.status_code == 200:
                                result_json = response.json()
                                modrinth_results = result_json.get("hits", [])
                            else:
                                error_message = f"Modrinth API Error: {response.status_code}"
                                logger.error(f"Modrinth Search Error: {response.text}")

                    except Exception as e:
                        logger.error(f"Failed to search Modrinth: {e}")
                        error_message = f"Search Error: {str(e)}"

                page_data["modrinth_query"] = search_query
                page_data["modrinth_results"] = modrinth_results
                page_data["current_type"] = resource_type
                page_data["current_version"] = user_version
                page_data["current_loader"] = loader_filter
                page_data["search_error"] = error_message

# rest of the file unchanged