import player
import powerup
import entities

entity_table = {
#  id: ( Serverclass , Clientclass   )
    1: (player.Player, player.CPlayer),
    2: (powerup.Powerup, powerup.CPowerup),
    3: (entities.HitMarker, entities.CHitMarker)
}