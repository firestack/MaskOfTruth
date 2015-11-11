
import twitchtools.chat.IRC_DB as IRCT
import twitchtools.chat.EventHandler as EH
from twitchtools.login.profiles import Profile
from twitchtools.chat import ChannelStorage as CS
import datetime
# Example classes

superUsers = ["bomb_mask"]


class BasicBanEvent(EH.EventHandler):
    TYPE = EH.TEvent.CLEARCHAT

    @classmethod
    def Execute(cls, ref, *message):
        data = ref.ChannelData(message[1].params.split(' ')[0])
        data.banAmount += 1

        ref.dftCursor.execute(
            "INSERT INTO bans VALUES (?,?,?)",
            (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'), message[1].GetMessage(), False)
        )

    @classmethod
    def Once(cls, ref):
        ref.CreateTable("bans", "Time TEXT, User TEXT, Us BOOL DEFAULT true")
        CS.ChannelData.banAmount = 0


class BasicStats(EH.EventHandler):
    TYPE = EH.TEvent.PRIVMSG

    @classmethod
    def Execute(cls, ref, *message):
        if message[1].GetMessage().lower() == "-hi":
            ref.PrivateMessage(message[1].params.split(' ')[0][1:], ref.ChannelData(message[1].params.split(' ',1)[0]).banAmount)

    @classmethod
    def Once(cls, ref):
        pass

class JoinCommand(EH.EventHandler):
    TYPE = EH.TEvent.PRIVMSG

    @classmethod
    def Execute(cls, ref, *message):

        if message[1].GetMessage().lower().startswith("-join ") and message[1].GetTags().get("display-name").lower() in superUsers:
            ref.Join(message[1].GetMessage().split(" ",2)[1])

class LeaveCommand(EH.EventHandler):
    TYPE = EH.TEvent.PRIVMSG

    @classmethod
    def Execute(cls, ref, *message):
        if message[1].GetMessage().lower().startswith("-leave ") and message[1].GetTags().get("display-name").lower() in superUsers:
            ref.Leave(message[1].GetMessage().split(" ",2)[1])

if __name__ == '__main__':
    twitch = IRCT.IRC_DB()

    twitch.Register(BasicBanEvent )
    twitch.Register(JoinCommand)
    twitch.Register(LeaveCommand)
    twitch.Register(BasicStats)

    twitch.flags["write"] = True
    cProfile = Profile("bombmask")
    twitch.username = cProfile.name
    twitch.password = cProfile.password
    twitch.serverPair = ("irc.twitch.tv", 6667)
    twitch.Start()
    twitch.Request("twitch.tv/tags")
    twitch.Request("twitch.tv/commands")


    twitch.Join("bomb_mask")


    #print("entering mainloop")
    try:
        twitch.MainLoop()
    except KeyboardInterrupt as E:
        pass

    twitch.Close()
