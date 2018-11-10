<?php

/**
 * Plugin Name: Participants Database Set Private ID Length
 * Description: Sets a custom length for the private ID
 * Author: Roland Barker (xnau), Customisation (length to 15 so that it cannot be bruteforced) by Fafadji GNOFAME. (Base code found here :https://gist.github.com/xnau/a65fc753d0101736b6739101f2a4982c )
 */
// set the private ID length to 15 (above 9 go to the table in DB and ajust the length of the field)
add_filter( 'pdb-private_id_length', function ( $length ) { return 15; } );
