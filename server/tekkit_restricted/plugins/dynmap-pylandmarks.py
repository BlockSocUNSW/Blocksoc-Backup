__plugin_name__ = "dynmap-PyLandmarks"
__plugin_version__ = "1.0"
__plugin_mainclass__ = "Landmarks"

# TODO: add minor version of landmarks for general users
#       every user may add x points of interest with a description and a specific icon via a special command
#       beacon,point of interest,mark
#       maybe add 'find' variant with reduced range, as well as some broadcasting capability to other players in range ("look here!","/mark find", looking at last player-created mark in range)
#       '/mark some_name' to add a mark
#       '/mark list' to list nearby marks sorted by range (higher range for proper landmarks, lower for player-created marks)
#       '/mark remove 0' to remove own marks
#       '/mark find 0' to look at one of the nearby marks

import os,math,re

from java.io import FileInputStream,File
from java.lang import String

from org.bukkit.util import Vector
from org.bukkit.configuration.file import YamlConfiguration
# boilerplate
import org.bukkit as bukkit
from java.util.logging import Level

server = bukkit.Bukkit.getServer()

log = server.getLogger()
CHAT_PREFIX = "[PyLandmarks] "
def info(*text):
    log.log(Level.INFO,CHAT_PREFIX+" ".join(map(unicode,text)))
def severe(*text):
    log.log(Level.SEVERE,CHAT_PREFIX+" ".join(map(unicode,text)))
def msg(player,*text):
    player.sendMessage(CHAT_PREFIX+" ".join(map(unicode,text)))

CONSOLE = server.getConsoleSender()
# end boilerplate

def lookat(entity,location):
    v = entity.getLocation().subtract(location)
    yaw = 360.0*math.atan2(v.getZ(), v.getX())/(2*math.pi)+90
    pitch = -(180.0*math.acos(v.getY()/v.length())/math.pi-90)
    target = entity.getLocation()
    target.setYaw(yaw)
    target.setPitch(pitch)
    entity.teleport(target)

class Landmarks(PythonPlugin):
    markerset = None
    default_type = "default"
    icons = {}
    disabled = False

    def __init__(self):
        PythonPlugin.__init__(self)
        self.api = None
        self.cfg = None
        self.folder = ""
        self.nameChecker = re.compile("^[a-zA-Z0-9\._]+$")

    def onEnable(self):
        self.findFolder()
        dynmap = server.getPluginManager().getPlugin("dynmap")
        if dynmap is not None and dynmap.isEnabled():
            self.api = dynmap.getMarkerAPI()
            Landmarks.markerset = self.api.getMarkerSet("pylandmarks") or self.api.createMarkerSet("pylandmarks","Landmarks",None,True)
            self.registerIcons()
            if not Landmarks.icons:
                severe("No icons found")
                Landmarks.disabled = True
            self.cfg = YamlConfiguration.loadConfiguration(File(os.path.join(self.folder,"config.yml")))
            Landmarks.default_type = self.cfg.getString("defaults.icon")
            if Landmarks.icons and Landmarks.default_type not in Landmarks.icons:
                Landmarks.default_type = Landmarks.icons.keys()[0]
                severe("Nonexistent icon set as default in config, using '%s' instead"%Landmarks.default_type)
            info("v%s enabled"%__plugin_version__)
        else:
            severe("Could not connect to dynmap")
            Landmarks.disabled = True
        return

    def findFolder(self):
        pluginfolder = os.path.split(self.dataFolder.toString())[0]
        for name in os.listdir(pluginfolder):
            if self.dataFolder.toString().lower() == os.path.join(pluginfolder,name).lower():
                self.folder = os.path.join(pluginfolder,name)

    def registerIcons(self):
        folder = os.path.join(self.folder,"icons")
        for image in os.listdir(folder):
            name,ext = os.path.splitext(image)
            if ext == ".png":
                name = name.lower()
                if not self.nameChecker.match(name):
                    continue
                stream = FileInputStream(os.path.join(folder,image))
                icon = self.api.getMarkerIcon("landmark_"+name)
                if icon is None:
                    icon = self.api.createMarkerIcon("landmark_"+name,name.capitalize(),stream)
                else:
                    icon.setMarkerIconImage(stream)
                stream.close()
                icon.setMarkerIconLabel(name)
                self.icons[name] = icon
        info("Loaded %s icons"%len(Landmarks.icons))

    def onDisable(self):
        pass

    @staticmethod
    def get(name):
        return Landmarks.markerset.findMarker(name)

    @staticmethod
    def create(name, world,x,y,z,type,label):
        return Landmarks.markerset.createMarker(name,label or name.capitalize(),world,x,y,z,Landmarks.icons[type],True)

@hook.command("lm",usage="/<command> list|set|type|label|remove|find|warp id [type|label]",description="Modify or use Landmarks")
def command(sender, args):
    console = not hasattr(sender,"getWorld")
    if Landmarks.disabled and cmd in ["set","type"]:
        msg(sender,"Most functionality is disabled at the moment, please contact your admin")
        return True
    if len(args) >= 1 and args[0] == "list" and (sender.hasPermission("pylandmarks.create") or sender.hasPermission("pylandmarks.modify")):
        lines = []
        if len(args) > 1 and args[1] == "types":
            lines.append("List of defined types:")
            for name in Landmarks.icons:
                lines.append(name)
            lines.append("%s types total"%len(Landmarks.icons))
        else:
            markers = [marker for marker in Landmarks.markerset.getMarkers()]
            lines.append("List of defined landmarks:")
            for marker in markers:
                lines.append("%s:%s (%s) @%s:%.1f|%.1f|%.1f"%(marker.getMarkerIcon().getMarkerIconLabel(),marker.getMarkerID(),marker.getLabel(),marker.getWorld(),marker.getX(),marker.getY(),marker.getZ()))
            lines.append("%s landmarks total"%len(markers))
        for line in lines:
            msg(sender,line)
        return True
    if len(args) < 2:
        return False
    cmd,id = args[0].lower(),args[1].lower()
    type = args[2].lower() if len(args) > 2 else ""
    typed = bool(type)
    if type not in Landmarks.icons:
        type = Landmarks.default_type
    label = " ".join(args[2:] if cmd == "label" else args[3:])

    world,x,y,z = None,0,0,0
    if console and cmd in ["set","warp","find"]:
        info("Command '%s' not available via console"%cmd)
        return True
    elif not console:
        world,x,y,z = sender.getWorld().getName(),sender.getLocation().getX(),sender.getLocation().getY(),sender.getLocation().getZ()

    marker = Landmarks.get(id)

    if cmd == "set" and sender.hasPermission("pylandmarks.create"):
        labeled = bool(label)
        if marker is None:
            marker = Landmarks.create(id,world,x,y,z,type,label)
            msg(sender,"Created marker '%s' of type '%s'"%(id,type)+labeled*(" labeled as '%s'"%label))
        else:
            marker.setLocation(world,x,y,z)
            if typed:
                marker.setMarkerIcon(Landmarks.icons[type])
            if labeled:
                marker.setLabel(label)
            msg(sender,"Set marker '%s' to your position"%id+(typed or labeled)*" and set "+typed*("type to '%s'"%type)+labeled*("and label to '%s'"%label))
    elif marker is None:
        msg(sender,"Marker '%s' does not exist"%id)
    else:
        if cmd == "type" and sender.hasPermission("pylandmarks.modify"):
            marker.setMarkerIcon(Landmarks.icons[type])
            msg(sender,"Set type of '%s' to '%s'"%(id,type))
        elif cmd == "label" and sender.hasPermission("pylandmarks.modify"):
            marker.setLabel(label)
            msg(sender,"Set label of '%s' to '%s'"%(id,label))
        elif cmd == "remove" and sender.hasPermission("pylandmarks.create"):
            marker.deleteMarker()
            msg(sender,"Removed marker '%s'"%id)
        elif cmd == "warp" and sender.hasPermission("pylandmarks.warp"):
            world,x,y,z = marker.getWorld(),marker.getX(),marker.getY(),marker.getZ()
            location = bukkit.Location(server.getWorld(world),x,y,z)
            location.setPitch(sender.getLocation().getPitch())
            location.setYaw(sender.getLocation().getYaw())
            sender.teleport(location)
            msg(sender,"You are now at '%s' (%s)"%(marker.getLabel(),id))
        elif cmd == "find" and sender.hasPermission("pylandmarks.find"):
            lookat(sender,bukkit.Location(server.getWorld(marker.getWorld()),marker.getX(),marker.getY(),marker.getZ()))
            msg(sender,"Now looking at '%s' (%s)"%(marker.getLabel(),id))
        else:
            msg(sender,"Unknown command '%s'"%cmd)
    return True