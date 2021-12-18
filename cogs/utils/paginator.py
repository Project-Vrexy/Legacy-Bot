from dislash import ActionRow, Button, ResponseType, ButtonStyle
import asyncio


# noinspection PyTypeChecker
class Paginator:
    def __init__(self, client, ctx, source, timeout=60):
        self.client = client
        self.ctx = ctx
        self.source = source
        self.timeout = timeout

        self.page = 0

    async def run(self):
        # emojis
        fpe = str(self.client.get_emoji(860503850644537344))
        ppe = str(self.client.get_emoji(860504570734837790))
        npe = str(self.client.get_emoji(860504617984196618))
        lpe = str(self.client.get_emoji(860504662397550612))
        ese = str(self.client.get_emoji(860504699954528277))

        cmd = self.ctx.message.id

        first_page = ActionRow(
            Button(emoji=fpe, custom_id=f"{cmd}:FirstPage", style=ButtonStyle.gray, disabled=True),
            Button(emoji=ppe, custom_id=f"{cmd}:PreviousPage", style=ButtonStyle.gray, disabled=True),
            Button(emoji=npe, custom_id=f"{cmd}:NextPage", style=ButtonStyle.blurple),
            Button(emoji=lpe, custom_id=f"{cmd}:LastPage", style=ButtonStyle.blurple),
            Button(emoji=ese, custom_id=f"{cmd}:GoBack", style=ButtonStyle.red),
        )

        regular_page = ActionRow(
            Button(emoji=fpe, custom_id=f"{cmd}:FirstPage", style=ButtonStyle.blurple),
            Button(emoji=ppe, custom_id=f"{cmd}:PreviousPage", style=ButtonStyle.blurple),
            Button(emoji=npe, custom_id=f"{cmd}:NextPage", style=ButtonStyle.blurple),
            Button(emoji=lpe, custom_id=f"{cmd}:LastPage", style=ButtonStyle.blurple),
            Button(emoji=ese, custom_id=f"{cmd}:GoBack", style=ButtonStyle.red),
        )

        last_page = ActionRow(
            Button(emoji=fpe, custom_id=f"{cmd}:FirstPage", style=ButtonStyle.blurple),
            Button(emoji=ppe, custom_id=f"{cmd}:PreviousPage", style=ButtonStyle.blurple),
            Button(emoji=npe, custom_id=f"{cmd}:NextPage", style=ButtonStyle.gray, disabled=True),
            Button(emoji=lpe, custom_id=f"{cmd}:LastPage", style=ButtonStyle.gray, disabled=True),
            Button(emoji=ese, custom_id=f"{cmd}:GoBack", style=ButtonStyle.red),
        )

        if len(self.source) == 1:
            return await self.ctx.reply(embed=self.source[self.page], mention_author=False)

        message = await self.ctx.reply(embed=self.source[self.page], components=[first_page], mention_author=False)
        on_click = message.create_click_listener(timeout=self.timeout)

        @on_click.not_from_user(self.ctx.author, cancel_others=True)
        async def on_wrong_user(inter):
            # Reply with a hidden message
            await inter.reply("You don't own this paginator session.", ephemeral=True)

        @on_click.matching_id(f"{cmd}:FirstPage")
        async def first(inter):
            self.page = 0
            await inter.reply(type=ResponseType.UpdateMessage, embed=self.source[0], components=[first_page])

        @on_click.matching_id(f"{cmd}:PreviousPage")
        async def prev(inter):
            self.page -= 1
            if self.page >= len(self.source) - 1:
                await inter.reply(type=ResponseType.UpdateMessage, embed=self.source[len(self.source) - 1],
                                  components=[regular_page])
            elif self.page < 0 or self.page == 0:
                await inter.reply(type=ResponseType.UpdateMessage, embed=self.source[0],
                                  components=[first_page])
            else:
                await inter.reply(type=ResponseType.UpdateMessage, embed=self.source[self.page],
                                  components=[regular_page])

        @on_click.matching_id(f"{cmd}:NextPage")
        async def _next(inter):
            self.page += 1
            if self.page > len(self.source) - 1 or self.page == len(self.source) - 1:
                await inter.reply(type=ResponseType.UpdateMessage, embed=self.source[self.page],
                                  components=[last_page])
            else:
                await inter.reply(type=ResponseType.UpdateMessage, embed=self.source[self.page],
                                  components=[regular_page])

        @on_click.matching_id(f"{cmd}:LastPage")
        async def last(inter):
            self.page = len(self.source) - 1
            await inter.reply(type=ResponseType.UpdateMessage, embed=self.source[self.page], components=[last_page])

        @on_click.matching_id(f"{cmd}:GoBack")
        async def _exit(inter):
            await inter.reply(type=ResponseType.UpdateMessage, embed=self.source[self.page], components=[])

        @on_click.timeout
        async def on_timeout():
            await message.edit(components=[])

    async def return_to(self, message, embed, components):
        await message.edit(embed=embed, components=components)
    
    async def replace(self, message, orig_embed=None, orig_comp=None):
        # emojis
        fpe = str(self.client.get_emoji(860503850644537344))
        ppe = str(self.client.get_emoji(860504570734837790))
        npe = str(self.client.get_emoji(860504617984196618))
        lpe = str(self.client.get_emoji(860504662397550612))
        ese = str(self.client.get_emoji(860504699954528277))
        gbe = str(self.client.get_emoji(887353238049939466))

        cmd = self.ctx.message.id

        if not orig_embed and not orig_comp:
            single_page = ActionRow(
                Button(emoji=ese, custom_id=f"{cmd}:GoBack", style=ButtonStyle.red)
            )
            
            first_page = ActionRow(
                Button(emoji=fpe, custom_id=f"{cmd}:FirstPage", style=ButtonStyle.gray, disabled=True),
                Button(emoji=ppe, custom_id=f"{cmd}:PreviousPage", style=ButtonStyle.gray, disabled=True),
                Button(emoji=npe, custom_id=f"{cmd}:NextPage", style=ButtonStyle.blurple),
                Button(emoji=lpe, custom_id=f"{cmd}:LastPage", style=ButtonStyle.blurple),
                Button(emoji=ese, custom_id=f"{cmd}:GoBack", style=ButtonStyle.red)
            )

            regular_page = ActionRow(
                Button(emoji=fpe, custom_id=f"{cmd}:FirstPage", style=ButtonStyle.blurple),
                Button(emoji=ppe, custom_id=f"{cmd}:PreviousPage", style=ButtonStyle.blurple),
                Button(emoji=npe, custom_id=f"{cmd}:NextPage", style=ButtonStyle.blurple),
                Button(emoji=lpe, custom_id=f"{cmd}:LastPage", style=ButtonStyle.blurple),
                Button(emoji=ese, custom_id=f"{cmd}:GoBack", style=ButtonStyle.red)
            )

            last_page = ActionRow(
                Button(emoji=fpe, custom_id=f"{cmd}:FirstPage", style=ButtonStyle.blurple),
                Button(emoji=ppe, custom_id=f"{cmd}:PreviousPage", style=ButtonStyle.blurple),
                Button(emoji=npe, custom_id=f"{cmd}:NextPage", style=ButtonStyle.gray, disabled=True),
                Button(emoji=lpe, custom_id=f"{cmd}:LastPage", style=ButtonStyle.gray, disabled=True),
                Button(emoji=ese, custom_id=f"{cmd}:GoBack", style=ButtonStyle.red)
            )
        else:
            single_page = ActionRow(
                Button(emoji=gbe, custom_id=f"{cmd}:GoBack", style=ButtonStyle.green)
            )
            
            first_page = ActionRow(
                Button(emoji=fpe, custom_id=f"{cmd}:FirstPage", style=ButtonStyle.gray, disabled=True),
                Button(emoji=ppe, custom_id=f"{cmd}:PreviousPage", style=ButtonStyle.gray, disabled=True),
                Button(emoji=npe, custom_id=f"{cmd}:NextPage", style=ButtonStyle.blurple),
                Button(emoji=lpe, custom_id=f"{cmd}:LastPage", style=ButtonStyle.blurple),
                Button(emoji=gbe, custom_id=f"{cmd}:GoBack", style=ButtonStyle.green)
            )

            regular_page = ActionRow(
                Button(emoji=fpe, custom_id=f"{cmd}:FirstPage", style=ButtonStyle.blurple),
                Button(emoji=ppe, custom_id=f"{cmd}:PreviousPage", style=ButtonStyle.blurple),
                Button(emoji=npe, custom_id=f"{cmd}:NextPage", style=ButtonStyle.blurple),
                Button(emoji=lpe, custom_id=f"{cmd}:LastPage", style=ButtonStyle.blurple),
                Button(emoji=gbe, custom_id=f"{cmd}:GoBack", style=ButtonStyle.green)
            )

            last_page = ActionRow(
                Button(emoji=fpe, custom_id=f"{cmd}:FirstPage", style=ButtonStyle.blurple),
                Button(emoji=ppe, custom_id=f"{cmd}:PreviousPage", style=ButtonStyle.blurple),
                Button(emoji=npe, custom_id=f"{cmd}:NextPage", style=ButtonStyle.gray, disabled=True),
                Button(emoji=lpe, custom_id=f"{cmd}:LastPage", style=ButtonStyle.gray, disabled=True),
                Button(emoji=gbe, custom_id=f"{cmd}:GoBack", style=ButtonStyle.green)
            )

        if len(self.source) == 1:
            await message.edit(embed=self.source[self.page], components=[single_page])
        else:
            await asyncio.sleep(1)
            await message.edit(embed=self.source[self.page], components=[first_page])
        on_click = message.create_click_listener(timeout=self.timeout)

        @on_click.not_from_user(self.ctx.author, cancel_others=True)
        async def on_wrong_user(inter):
            # Reply with a hidden message
            await inter.reply("You don't own this paginator session.", ephemeral=True)

        @on_click.matching_id(f"{cmd}:FirstPage")
        async def first(inter):
            self.page = 0
            await inter.reply(type=ResponseType.UpdateMessage, embed=self.source[0], components=[first_page])

        @on_click.matching_id(f"{cmd}:PreviousPage")
        async def prev(inter):
            self.page -= 1
            if self.page >= len(self.source) - 1:
                await inter.reply(type=ResponseType.UpdateMessage, embed=self.source[len(self.source) - 1],
                                  components=[regular_page])
            elif self.page < 0 or self.page == 0:
                await inter.reply(type=ResponseType.UpdateMessage, embed=self.source[0],
                                  components=[first_page])
            else:
                await inter.reply(type=ResponseType.UpdateMessage, embed=self.source[self.page],
                                  components=[regular_page])

        @on_click.matching_id(f"{cmd}:NextPage")
        async def _next(inter):
            self.page += 1

            if self.page > len(self.source) - 1 or self.page == len(self.source) - 1:
                await inter.reply(type=ResponseType.UpdateMessage, embed=self.source[self.page],
                                  components=[last_page])
            else:
                await inter.reply(type=ResponseType.UpdateMessage, embed=self.source[self.page],
                                  components=[regular_page])

        @on_click.matching_id(f"{cmd}:LastPage")
        async def last(inter):
            self.page = len(self.source) - 1
            await inter.reply(type=ResponseType.UpdateMessage, embed=self.source[self.page], components=[last_page])

        @on_click.matching_id(f"{cmd}:GoBack")
        async def _back(inter):
            await inter.reply(type=6)
            if orig_comp and orig_embed:
                await self.return_to(message=message, components=orig_comp, embed=orig_embed)
                on_click.kill()
            else:
                await message.edit(components=[])

        @on_click.timeout
        async def on_timeout():
            await message.edit(components=[])
