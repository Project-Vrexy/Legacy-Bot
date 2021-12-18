class CustomChecks:
    def __init__(self, client):
        self.client = client


class WaitForChecks:
    def __init__(self, client, ctx):
        self.client = client
        self.ctx = ctx

    def aligned_ctx(self, messages):
        return messages.author.id == self.ctx.author.id and messages.channel.id == self.ctx.channel.id

    def owner_is_sure(self, messages):
        return messages.author.id == self.ctx.author.id and messages.channel.id == self.ctx.channel.id and \
               messages.content == 'y'

    def correct_button(self, messages):
        return messages.author.id == self.ctx.author.id and messages.channel.id == self.ctx.channel.id
