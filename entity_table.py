import player
import powerup

entity_table = {
#  id: ( Serverclass , Clientclass   )
    1: (player.Player, player.CPlayer)
    2: (powerup.Powerup, powerup.CPowerup)
}