import shutil, enum


class eCareDirection( enum.Enum ):
    CARE_LEFT   = 0,
    CARE_RIGHT  = 1,
    CARE_BOTH   = 2


to_prune = [ "./prune.py", "recorbra2.py" ]
charinfo_map = {
    "(": {  "dont_repel": [ ")", " " ], "care": eCareDirection.CARE_RIGHT,    "space": " "  },
    ")": {  "dont_repel": [ "(", " " ], "care": eCareDirection.CARE_LEFT,     "space": " "  },
    "[": {  "dont_repel": [ "]", " " ], "care": eCareDirection.CARE_RIGHT,    "space": " "  },
    "]": {  "dont_repel": [ "[", " " ], "care": eCareDirection.CARE_LEFT,     "space": " "  },
    "=": {  "dont_repel": [ "=", " " ], "care": eCareDirection.CARE_BOTH,     "space": " "  }
}

for file_name in to_prune:
    file = open( file_name, "r+" ); lines = file.readlines(); file.close()
    shutil.copy( file_name, file_name + ".backup" )

    for y in range( 0, len( lines ) - 1 ):
        quote_char = [ "\"", "'" ]; quote_mode = ""; comment_mode = False

        for x in range( 0, len( lines[ y ] ) ):
            try: 
                charinfo_map[ lines[ y ][ x ] ]
            
            except KeyError:
                # Calculate "quote-mode", detects if we're in a string
                if lines[ y ][ x ] in quote_char:
                    if ( not quote_mode ):
                        quote_mode = lines[ y ][ x ]
                    elif ( quote_mode == lines[ y ][ x ] ):
                        quote_mode = ""

                # Calculate comment-mode
                if ( lines[ y ][ x ] == "#" ) and ( not quote_mode ):
                    comment_mode = True
                    
                continue  # Next char
            char_info = charinfo_map[ lines[ y ][ x ] ]

            # Calculate what needs to be "repelled"
            repel_left_needed = False; repel_right_needed = False
            if x and ( char_info[ "care" ] == eCareDirection.CARE_LEFT ):
                if ( lines[ y ][ x - 1 ] not in char_info[ "dont_repel" ] ):
                    repel_left_needed = True
            if ( x < ( len( lines[ y ] ) - 2 ) ) and ( char_info[ "care" ] == eCareDirection.CARE_RIGHT ):
                if ( lines[ y ][ x + 1 ] not in char_info[ "dont_repel" ] ):
                    repel_right_needed = True
            if ( char_info[ "care" ] == eCareDirection.CARE_BOTH ):
                if ( lines[ y ][ x - 1 ] not in char_info[ "dont_repel" ] ):
                    repel_left_needed = True
                if ( lines[ y ][ x + 1 ] not in char_info[ "dont_repel" ] ):
                    repel_right_needed = True
            
            # Display info
            if ( repel_left_needed or repel_right_needed ) and ( not comment_mode ) and ( not quote_mode ):
                out_line = "(" + str( x ) + ", " + str( y ) + "): "
                print( out_line + lines[ y ][ :-1 ] )
                print( ( " " * ( x + len( out_line ) ) ) + "^" )
                
                """
                if repel_left_needed:
                    print( "Before: '" + lines[ y ][ x - 1 ] + "'" )
                elif repel_right_needed:
                    print( "After: '" + lines[ y ][ x + 1 ] + "'" )
                """
            
                if repel_right_needed:
                    lines[ y ] = lines[ y ][ :x + 1 ] + char_info[ "space" ] + lines[ y ][ x + 1: ]
                if repel_left_needed:
                    lines[ y ] = lines[ y ][ :x ] + char_info[ "space" ] + lines[ y ][ x: ]
    
    # Finally rewrite file
    file = open( file_name, "w" )
    file.writelines( lines )
    file.close()

