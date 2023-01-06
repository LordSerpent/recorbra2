#!/usr/bin/python
# -*- coding: utf-8 -*-

# recorbra2
# Python 3.10

"""
A bot that archives as much content as possible on a YouTube channel

A thank you to everyone that has ever contributed to youtube-dl or yt-dlp. Without their tools this bot wouldn't be possible.
"""


# Built-in Libraries
import argparse
import os
import json
import shutil
import subprocess
import requests
import yt_dlp

from recorbra_common import *


# Global Variables

# Python __vars__
__license__ = "GNU General Public License v3.0"
__copyright__ = "Copyright 2022, recorbra"
__repo__ = "https://github.com/LordSerpent/recorbra2"
__contacts__ = [
	( 	"Email",			"lordserpent@protonmail.com"										 ),
	( 	"GitHub",			"LordSerpent"														 )
]
__credits__ = [
	( 	"Author",			"LordSerpent"														 ),
	( 	"youtube-dl",		"https://github.com/ytdl-org/youtube-dl/graphs/contributors"		 ),
	( 	"yt-dlp",			"https://github.com/yt-dlp/yt-dlp/graphs/contributors"				 )
]
YTDLAPP = "ytdl"


def get_id_from_url( url ):
	# URL template
	# https://www.youtube.com/channel/<channel-id>
	# https://www.youtube.com/@<channel-handle>

	ytdl_opts = {}
	with yt_dlp.YoutubeDL(ytdl_opts) as ytdl:
		channel_info = ytdl.extract_info(url, download = False)
		with open("temp.json", "w") as outfile:
			json.dump( ytdl.sanitize_info( channel_info ), outfile, indent = 4 )
		
	return channel_info[ "channel_id" ]


def get_ytdlapp():
	if YTDLAPP not in os.listdir():
		print( "YouTube-DL missing, downloading now...", end = "\n" )

		# To-do, have the script check the OS and download the appropriate binary
		response = requests.get( "https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp" )

		with open( YTDLAPP, "wb" ) as ytdlapp_bin:
			ytdlapp_bin.write( response.content )
		print( "Done" )


def cl_args():
	"""Returns arguments in an argpase object"""

	parser = argparse.ArgumentParser( prog = "recorbra2", description = "A tool for archiving YouTube channels", epilog = "Help-text" )
	parser.add_argument( "mode", action = "store", type = str, help = "N/A" )

	# parser.add_argument( "--library-name", "--lib-name", "--ln", action = "store", type = str, help = "N/A" )
	# parser.add_argument( "--library-path", "--lib-path", "--lp", action = "store", type = str, help = "N/A" )
	# parser.add_argument( "--library-display-name", "--lib-disp-name", "--ldn", action = "store", type = str, help = "N/A" )
	
	# parser.add_argument( "--channel-url", "--chan-url", "--cu", action = "store", type = str, help = "N/A" )
	# parser.add_argument( "--channel-id", "--chan-id", "--ci", action = "store", type = str, help = "N/A" )
	
	parser.add_argument( "--lib-name",		dest = "library_name",			action = "store", type = str, help = "N/A" )
	parser.add_argument( "--lib-path",		dest = "library_path",			action = "store", type = str, help = "N/A" )
	parser.add_argument( "--lib-disp-name",	dest = "library_display_name",	action = "store", type = str, help = "N/A" )

	parser.add_argument( "--chan-url",		dest = "channel_url",			action = "store", type = str, help = "N/A" )
	parser.add_argument( "--chan-id",		dest = "channel_id",			action = "store", type = str, help = "N/A" )

	parser.add_argument( "--version", "--ver", "-v", action = "version", version = "%(prog)s 1.0", help = "N/A" )

	args = parser.parse_args()
	
	# Treat arguments
	args.mode = args.mode.upper().replace( "-", "_" )

	if args.library_name:
		args.library_name = args.library_name.lower()
	if not args.library_display_name:
		args.library_display_name = args.library_name
	
	if ( not args.channel_id ) and ( args.channel_url ):
		args.channel_id = get_id_from_url( args.channel_url )
	
	"""
	elif ( not args.channel_url ) and ( args.channel_id ):
		args.channel_url = get_url_from_id( args.channel_id )
	"""

	return args


def update_master( newcontent_dict ):
	master_path = RECORBRA_ROOT + "master_record.json"
	final_dict = json.load( open( master_path, ) ) | newcontent_dict

	json_object = json.dumps( final_dict, indent = 4 )

	# Now write the updated master file
	master_file = open( master_path, "w" )
	master_file.write( json_object )
	master_file.close()


def get_master():
	return json.load( open( RECORBRA_ROOT + "master_record.json", ) )


def mode_monitor( args ):
	"""N/A"""

	print( "Monitoring here should be here" )


def mode_dellibrary( args ):
	master = get_master()

	# Check library exists
	try:
		lib = master[ "libraries" ][ args.library_name ]
	except KeyError:
		print( "Library '" + args.library_name + "' cannot be found, so can't be deleted" )
		return 1

	# Remove folder
	try:
		shutil.rmtree( lib[ "path" ] )
	except FileNotFoundError:
		None
		
	# Finally remove the library from the master-record
	del master[ "libraries" ][ args.library_name ]
	update_master( master )

	print( "Library '" + args.library_name + "' has been removed" )


def mode_addlibrary( args ):
	"""N/A"""

	# Temp
	# mode_dellibrary( args )

	# Check args are ready
	if not args.library_name:
		print( "Missing library name, please use --library-name" )
		return 1
	if not args.library_path:
		print( "Missing library path, please use --library-path" )
		return 1

	# Check library doesn't already exists
	if args.library_name in get_master()[ "libraries" ].keys():
		print( "A library with the name '" + args.library_name + "' already exists" )
		return

	# Create the library folder and it's library record
	args.library_path = treat_path( args.library_path, eTreatPathType.TREATPATH_FOLDER ) + args.library_name + "/"
	try:
		os.mkdir( args.library_path )
	except FileExistsError:
		print( "Library already exists, please remove '" + args.library_name + "' or choose another location" )
		return 1

	# Prepare the library JSON object
	library_dict = {}
	library_dict[ "library_name" ] = args.library_name
	# library_dict[ "state" ] = "standby"
	library_dict[ "channels" ] = []
	os.chdir( args.library_path )
	json_object = json.dumps( library_dict, indent = 4 )

	# Then write the object to the library record file 
	library_file = open( "library.json", "w" )
	library_file.write( json_object )
	library_file.close()

	# Update the master record
	new_content = {
		"libraries": {
			args.library_name: {
				"path": treat_path( os.getcwd(), eTreatPathType.TREATPATH_FOLDER ),
				"channels": {},
				"internal_name": args.library_name,
				"display_name": args.library_display_name
			}
		}
	}
	
	update_master( new_content )

	# Move back to the directory we started in
	os.chdir( RECORBRA_ROOT )

	print( "Library '" + args.library_name + "' has been created" )


def mode_addchannel( args ):
	"""N/A"""

	# Check it isn't already being archived
	if args.channel_id in get_master()[ "libraries" ][ args.library_name ][ "channels" ].keys():
		print( "Channel already being archived to this library (" + args.library_name + ")" )
		return 1

	# Update the master record
	new_content = {
		"libraries": {
			args.library_name: {
				"channels": {
					args.channel_id: {}
				}
			}
		}
	}
	update_master( new_content )


def mode_help( args ):
	print( "HELP TEXT HERE" )
	print( args )


def mode_none( args ):
	None


def main():
	"""main"""

	global RECORBRA_ROOT

	mode_map = {
		"NONE":					mode_none,  # Temp
		"HELP":					mode_help,
		
		"MONITOR":				mode_monitor,

		"ADD_LIBRARY":			mode_addlibrary,
		"ADD_LIB":				mode_addlibrary,
		"DEL_LIBRARY":			mode_dellibrary,
		"DEL_LIB":				mode_dellibrary,

		"ADD_CHANNEL":			mode_addchannel,
		"ADD_CHAN":				mode_addchannel,
	}

	# Prepare command-line arguments
	RECORBRA_ROOT = treat_path( os.getcwd(), eTreatPathType.TREATPATH_FOLDER )
	args = cl_args()

	# Check the YouTube downloader exists on this system
	# get_ytdlapp()

	# Go in to whatever mode was specified
	mode_map[ args.mode ]( args )


if __name__ == "__main__":
	exit( main() )