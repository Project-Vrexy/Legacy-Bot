import nextcord as discord
from cogs.utils.paginator import Paginator
from traceback import walk_tb


class HelpUtils:
    def __init__(self, client):
        self.client = client

    # async def get_aliases(self, command, embed=None, inline=True):
    #     if not command.aliases:
    #         return
    #
    #     aliases = [alias for alias in command.aliases]
    #     aliases.sort()
    #
    #     if embed is None:
    #         return f"**Aliases**: {', '.join(aliases)}"
    #     else:
    #         return embed.add_field(
    #             name="Aliases",
    #             value=', '.join(aliases),
    #             inline=inline,
    #         )
    #
    @staticmethod
    async def get_command_usage(context, command, return_usage=False):
        command_qualified_name = command.name
        parent_qualified_name = command.parent.name if command.parent else None

        ret = f"{parent_qualified_name} {command_qualified_name}" if parent_qualified_name is not None else \
            command_qualified_name

        if return_usage and command.usage != " " and command.usage:
            ret += f" {command.usage}"
        return f"{context.prefix}{ret}"

    @staticmethod
    async def get_command_signature(ctx, command, return_usage=False):
        if command.aliases:
            command.aliases.sort()

            command_qualified_name = f"[{command.name}|{'|'.join(command.aliases)}]"
        else:
            command_qualified_name = command.name

        if command.parent:
            if command.parent.aliases:
                command.parent.aliases.sort()

                parent_qualified_name = f"[{command.parent.name}|{'|'.join(command.parent.aliases)}]"
            else:
                parent_qualified_name = command.parent.name
        else:
            parent_qualified_name = None

        ret = f"{parent_qualified_name}{command_qualified_name}" if parent_qualified_name is not None else \
            command_qualified_name

        if return_usage and command.usage != " " and command.usage:
            ret += f" {command.usage}"
        return f"{ctx.prefix}{ret}"

    @staticmethod
    async def page_split(_list, split):
        return [_list[x:x + split] for x in range(0, len(_list), split)]

    @staticmethod
    async def get_clean_checks(ctx, command, embed=None):
        if not command.checks:
            return None

        try:
            check = command.checks[0]
            check(0)
        except Exception as err:
            frames = [*walk_tb(err.__traceback__)]
            last_trace = frames[-1]
            frame = last_trace[0]

            try:
                perm = frame.f_locals['perms']

                fk = [key.replace("_", " ").title() for key in perm.keys()]

                if embed is None:
                    return f"Requires the `{', '.join(fk)}` permission(s)"
                else:
                    return embed.add_field(name="Requires Permissions", value=', '.join(fk))
            except KeyError:
                return None

    @staticmethod
    async def get_required_env(ctx, command, embed=None):
        ret = []

        if 'extras' in dir(command.cog) and command.name in command.cog.extras:
            if 'is_nsfw' in command.cog.extras[command.name]:
                if embed:
                    ret.append(embed.add_field(name="Is NSFW", value="Yes"))
                else:
                    ret.append("This command is NSFW.")

            if 'guild_only' in command.cog.extras[command.name]:
                if embed:
                    ret.append(embed.add_field(name="Guild Only", value="Yes"))
                else:
                    ret.append("This command cannot be used in DMs.")

        return ret

    async def examples(self, context,  command, embed=None):
        try:
            if command.parent:
                example = command.cog.extras[command.parent.name][command.name]['examples']

            else:
                example = command.cog.extras[command.name]['examples']

            f_example = [
                f"`{item.replace('PlaceDet', f'{await self.get_command_signature(context, command)}')}`"
                for item in example
            ]

            if embed is None:
                ret = '\n'.join(f_example)
            else:
                ret = embed.add_field(name="Example", value='\n'.join(f_example))
        except (KeyError, AttributeError):
            title = f"{command.parent} {command.name}" if command.parent else command.name
            if "PlaceDet" in command.description:
                if embed is not None:
                    ret = embed.add_field(name="Example", value=command.description.replace('PlaceDet', context.prefix))
                else:
                    ret = command.description.replace('PlaceDet', context.prefix)
            elif embed is None:
                ret = f"`{context.prefix}{title} {command.description}`"

            elif not command.description:
                ret = ""
            else:
                ret = embed.add_field(name="Example", value=f"`{context.prefix}{title} {command.description}`")
        return ret


class HelpMenus:
    def __init__(self, client):
        self.client = client
        self.utils = HelpUtils(client)

    async def paginated_menu(self, context, group_get, title, description, split_per_page=5):
        group = self.client.get_command(name=group_get)
        filtered_commands = [command.name for command in group.commands]

        filtered_commands.sort()
        filtered_commands.insert(0, group_get)

        split_commands = await self.utils.page_split(filtered_commands, split_per_page)
        pages = []

        for i in range(len(split_commands)):
            command_chunks = split_commands[i]

            e = discord.Embed(
                title=title,
                color=discord.Color.green(),
                description=description
            )

            for listed_command in command_chunks:
                if listed_command != group_get:
                    command = group.get_command(name=listed_command)
                else:
                    command = self.client.get_command(name=group_get)

                cmd_data = []

                if command.description and command.description != " ":
                    cmd_data.append(f"**Example:** `{context.prefix}{context.command.name} {command.name} "
                                    f"{command.description}`")

                n = '\n'
                e.add_field(
                    name=f"`{await self.utils.get_command_signature(context, command)}`",
                    value=f"```yaml\n{command.brief}```{n.join(cmd_data)}",
                    inline=False
                )

            e.set_footer(text=f"<> - Required • [] - Optional."
                              f"\nPage {i + 1}/{len(split_commands)} • {len(command_chunks)}/{len(filtered_commands)} "
                              f"commands.")

            pages.append(e)

        pag = Paginator(self.client, context, pages)
        await pag.run()

    async def menu(self, context, group_get, title, description):
        e = discord.Embed(
            title=title,
            color=discord.Color.green(),
            description=description
        )

        group = self.client.get_command(name=group_get)
        filtered_commands = [command.name for command in group.commands]

        filtered_commands.sort()
        filtered_commands.insert(0, group_get)

        for command in filtered_commands:
            if command != group_get:
                cmd = group.get_command(name=command)
            else:
                cmd = self.client.get_command(name=group_get)

            cmd_data = []

            if cmd.description and cmd.description != " ":
                cmd_data.append(f"**Example:** `{context.prefix}{context.command.name} {cmd.name} {cmd.description}`")

            n = '\n'
            e.add_field(
                name=f"`{await self.utils.get_command_signature(context, cmd, return_usage=True)}`",
                value=f"```yaml\n{cmd.brief}```{n.join(cmd_data)}", inline=False
            )

        e.set_footer(text=f"<> - Required • [] - Optional."
                          f"\n{len(filtered_commands)} commands.")
        await context.reply(mention_author=False, embed=e)
