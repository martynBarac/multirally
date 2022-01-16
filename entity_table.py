import player
import powerup
import entities

entity_table = {
#  id: ( Serverclass , Clientclass   )
    1: (player.Player, player.CPlayer),
    2: (powerup.Powerup, powerup.CPowerup),
    3: (entities.HitMarker, entities.CHitMarker),
    4: (entities.DebugTarget, entities.CDebugTarget)
}

static_entity_table = {
    "LaserWall": (entities.LaserWall, entities.CLaserWall)
}
