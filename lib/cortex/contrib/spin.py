spin_script_version = "0007" 
###############################################################################
# DO NOT hand-edit the above line.
# It will be updated automatically when you use THIS script to save THIS file!
###############################################################################
# The above version number is used to detect the existence of an updated file.
# Since this script is also saved as a file to the ftp site, its version number
# is retrieved from the spin$map and compared to the version number above.
# The user is notified when the spin$map says a newer version number exists.
###############################################################################
# Created       : 14 May 99
# Released      : 26 Jul 99 - V 0002
# Modified      : 12 Nov 99 - V 0003
#                           Add option to select binary/ascii ftp transfer mode
#                               and auto-detect .gif, and .jpg files.
#                           Add option to force the creation of a new spin$map
#                               entry even if a file with the same name is
#                               already registered for a different entry.
#                           Fix bug detecting pre-existence of target directory.
#                           Trim off some of the informational screen messages.
#                           Upgrade to allow file name to include a path.
# Modified      : 12 Feb 01 - V 0004
#                           Auto-detect .zip files for binary ftp transfer mode
#                           Change to recognize "no" as "N" in operator's input
#                           (or in fact anything that starts with "N" or "n",
#                            even with leading spaces). Same thing for "Y".
# Modified      : 14 Apr 05 - V 0005
#                           Auto-detect .pdf, .bmp .pdf .xls .tar .gz file types
#                           for binary ftp transfer mode
#                           Add command line arguments -archive_node (or -rn)
#                           and -archive_dir (or -rd) to specify an alternate 
#                           archival location.
# Modified      : 28 Aug 07 - V 0006
#                           the ftp software (maybe the target node) on www.pa.msu.edu 
#                           has changed, and now returns the full name with path 
#                           at the nlst command, which made spin think that 
#                           the target directory did not exist
# Modified      : 18 Mar 10 - V 0007
#                           switch ftp host from www.pa.msu.edu to ftp.pa.msu.edu
#                           and increase robustness against flavors of ftp.nlst()
###############################################################################
#  To do:
#  - Add update to some DZero ftp account
#  - some kind of spin get command?
#  - some kind of spin diff command?
#  - implement the Y/N update flags
#  - Add automatic update of Trics files to MSUl1a and D0TCC1
#  - upgrade spin_map_generator to read current version number from archival site.
#  - use call to set target file names in spin_map_record_parser
# \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
# ////////////////////////////////////////////////////////////////////////
# These few lines get printed no matter what the command line

print '.'
print '             DZero Trigger Run II'
print '              Spin Command File'
print '                -------------'
print '       Web Documentation Update Utility'
print '                    V' + spin_script_version
print '                -------------'

#\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
# Print Usage information

def Spin_Help ():
#---------------
    print """
 Spin Usage:

   Type the following command from a directory containing the source file
   to update and the spin script or specify explicit path names

      python spin.py <filename>             for an explicit filename
   or python spin.py                        will find the last modified file
                                                in the current directory
                                                and ask for source file name

      python spin.py -binary|-b [filename]  will force binary ftp transfer mode
      python spin.py -ascii|-a [filename]   will force ascii ftp transfer mode
      python spin.py -new|-n [filename]     will force a new spin$map entry

      python spin.py -help|-h|-?|?          will display this information
      python spin.py -doc|-d                will display the spin documentation

   additional optional arguments for special cases :
      -archive_node|-rn [node.ip.address]   override the archival node address
      -archive_dir|-rd [arch_dir]           override the remote directory name 
"""
    raw_input( '<CR>' )
    print """
   The spin.py python script can be downloaded from
        http://www.pa.msu.edu/hep/d0/ftp/spin/spin.py
     or ftp://www.pa.msu.edu/pub/d0/spin/spin.py

   On a machine with the DZero NT software installed
    first type the following setup commands
            bash                at the MS-DOS command prompt
      then  setup python        at the bash prompt
      then  python spin.py...

   Depending on the version of python installed on the local machine,
   you may need to also copy the getpass.pyc file from the same area
   of the trigger documentation home ftp site and place this file
   in the same directory as the spin python script.
"""

#\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
# Print the Spin Documentation

def Spin_Doc ():
#---------------
    print """

 Purpose of the Spin utility:

   Create or update a trigger documentation file by placing a copy of the file
   - onto the main trigger documentation ftp/http server at MSU
       (which is the primary source for Run II trigger documentation)
   - and onto the (separate) arhival ftp site at MSU
       (with a modified file name for versioning purpose)
   - and onto the mirror fnal ftp directory (not yet implemented)
       (to guarantee access to the documentation at all times while at DZero)
   - while automatically placing the file in its correct directory location
       (the proper target directory is deduced from the file name alone)
"""
    raw_input( '<CR>' )
    print """
 An additional goal of the Spin utility is to allow the user to update the
 trigger documentation from any PC or Sun Workstation (or other platform)
 located at MSU or Dzero (or elswhere).
 The Spin utility is written using the Python scripting language which
 is implemented on a variety of operating systems including
 Windows NT and Solaris (available for free from www.python.org).

 The user would typically view and get a copy of the latest version of
 a particular documentation file with a Web Browser (e.g. Netscape)
 accessing http://www.pa.msu.edu/hep/d0, then, after locally modifying
 the file, use Spin to automatically put this updated version back in
 the directory where the original version came from.  If necessary
 the user can obtain the spin python script from the /hep/d0/ftp/spin
 directory on the same web server.
"""
    raw_input( '<CR>' )
    print """
 To remember the assigned target location of each trigger documentation file
 as well as its last modification date and version number, Spin uses a Spin$Map
 file also located on the primary home ftp site.  Spin retrieves, updates and
 replaces this Spin$Map file every time a documentation file is being updated.
 The files are indexed in the Spin$Map by their file name only.
 The target directory name is part of a file entry but cannot be used in the
 key name since any file can be updated from any local directory.
 It is thus strongly recommended (but not required) to use distinct file names
 for all trigger documentation files.  Ambiguities will be pointed out by
 spin and the user will be ask to decide which of the possible destinations is
 the correct one, which somewhat defeats the purpose of this utility.
"""
    raw_input( '<CR>' )
    print """
 Detailed steps of the Spin script:

   - get a listing of the current directory
   - if no target file was specified on the command line find
       the most recently modified file in the local default directory
       then ask the user for confirmation or a different file name
   - verify that the file name corresponds to an existing file
   - if the file name is not all lowercase, notify the user it will be made so
   - open an ftp connection to the home ftp site
       ask user for password to access the trigger account on this machine
   - open an ftp connection to the archival ftp site
       ask user for password to access the trigger account on this machine
       offers <CR> if password is identical as previous one.
   - If either one of these two connection attempts fails, abort.
   - Retrieve the spin$map file from the home ftp site and parse its records
       looking for entries for (1) the target file (2) the spin pyhton script
       and (3) the spin$map itself
   - abort if no record is found for the spin script or the spin$map
   - compare the version number defined in the first line of the running spin
       script to the version number for the spin script found in the spin$map
       and warn that a more recent script exists if necessary with the
       recommended option to bail out and obtain the newest spin script.
"""
    raw_input( '<CR>' )
    print """
   - It is a special case if it is the spin script itself that is being updated
       in order to insure that the internal version number recorded in a
       variable of the spin python script matches the version number it will
       be archived as and tagged as in the spin$map.  A temporary local copy
       of spin.py will be created where the first line is overriden to specify
       the desired version number.
   - If no record was found for the target file in the spin$map, offer the
       option to create a new one.
   - Summarize and display all the known information about the file to update
       and ask for final confirmation
   - Send the target file to the home ftp site, but first verify that the
       target directory exists and recursively create each subdirectory
       level if necessary asking for confirmation each time.
   - Send the target file to the archival ftp site using the same subdirectory
       path while creating subdirectories as needed without asking, but
       append the version number to the file name in order not to overwrite
       older versions of the same file (e.g. file_name.file_ext.0006)
   - send the updated spin$map file to the home ftp site
   - send the updated spin$map file to the archival ftp site, also with its
       updated version number appended to the spin$map file name
"""
    raw_input( '<CR>' )
    print """
  Misc Notes:
   - spin forces all file names to lowercase before saving them or
   - a file entry in the spin$map consists of
           the file's name used as the key to locate the record
           the file's target directory
           a Y/N flag specifying the file was successfully archived
               the last time it was updated with spin (not yet used)
           a Y/N flag specifying the file was successfully copied to fermilab
               the last time it was updated with spin (not yet used)
           the file version number as recorded on the archival site
           the date and time of the last time it was updated with spin
   - it seems like the getpass python module used to ask for user password
       without echoing the password entered on the keyboard does not work
       properly on Solaris
   - there is a special command line option spin -generate_map to create
       a new spin$map file on the local node just by scanning the file on the
       ftp home site.  All files are currently registered with version 0000,
       and this option will later be upgraded to query the archival ftp site
       and find the proper latest version number.
"""

# \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
# ////////////////////////////////////////////////////////////////////////

import sys
import os
import ftplib
import string
import tempfile
import time
import getpass  #distributed with python v1.5.2 (
                #or can be copied to use with older versions)

#######################################
# location of main home WWW area
#(for screen messages only; no HTTP access is done here)
#######################################

home_http_ip_address = 'www.pa.msu.edu'
home_http_head_dir   = 'hep/d0/'

#######################################
# location of main home FTP area
# or enter home_ftp_ip_address = 'localhost'
# to aim at a local directory tree for spin code development
#######################################

# Official Home
home_ftp_ip_address = 'ftp.pa.msu.edu'
home_ftp_head_dir   = 'www/'                    # link to DZero Web area as seen from trigger account

# account to use for access to home ftp site
home_ftp_user       = 'trigger'
home_ftp_password   = ''  # this will be entered intereactively; don't change

# for development, no FTP
#home_ftp_ip_address = 'localhost'
#home_ftp_head_dir    = 'C:/Users/Python/localhost/home/'  # Case sensitive for local host

# for development, with FTP
#home_ftp_ip_address  = 'ribbit.pa.msu.edu'
#home_ftp_head_dir    = 'F:/www_TRG/1999_03_05/'

#######################################
# location of Archival FTP area
#######################################

# Official Home
archive_ftp_ip_address = 'ribbit.pa.msu.edu'
archive_ftp_head_dir   = 'F:/www_TRG/Archive/'

# account to use for access to archival ftp site
archive_ftp_user       = 'trigger'
archive_ftp_password   = ''  # this will be entered intereactively; don't change

# for development, no FTP
#archive_ftp_ip_address = 'localhost'
#archive_ftp_head_dir   = 'C:/Users/Python/localhost/archive/' # Case sensitive for local host

# for development, with FTP
#archive_ftp_ip_address = 'ribbit.pa.msu.edu'
#archive_ftp_head_dir   = 'F:/www_TRG/1999_03_05/'

#######################################
# location of some key fixed files
#######################################

# location and name of this script
spin_script_name    = 'spin.py'
spin_script_dir     = 'ftp/spin/'

# same thing for the spin map on the ftp server
spin_map_name       = 'spin$map'
spin_map_dir        = spin_script_dir

#######################################
# miscellaneous control parameters
#######################################

#file buffer size used for binary file transfers
file_buffer_size = 4096

#define the following variable (to any value) to ask for <CR> before exiting
wait_on_exit = 1

############################################################################
############################################################################
############################################################################


############################################################################
# handle ftp connection and reading / writing files
############################################################################

class ftp_connection:
#====================
# handle basic ftp steps for connecting, and reading/writing a file

    last_pwd_cached = '' # cache the last password entered

    def __init__ ( self ) :
        #------------------

        self.confirm_dir_creation = 'Y'

    def open ( self, host, user ):
        #-------------------------

        self.host = host
        self.user = user
        self.connected = 'N'

        if ( self.host != 'localhost' ) :

            if ( ftp_connection.last_pwd_cached != '' ) :
                print '(Enter <CR> for same pwd as previous)'

            while 1 :

                self.password = getpass.getpass ( 'Enter Password for ' + self.user +
                                                  ' on ' + self.host + ' : ' )
                if ( self.password == '' ) :
                    self.password = ftp_connection.last_pwd_cached

                try :
                    print 'ftp/opening <' + self.host + '> as <' + self.user + '>'
                    self.ftp = ftplib.FTP ( self.host, self.user, self.password )
                    print self.ftp.getwelcome()

                except ftplib.error_perm, detail :
                    print 'Permission Error: ', detail
                    continue # try enter password again

                except ftplib.socket.error, detail :
                    print 'Socket Error :', detail
                    break

                else:
                    self.connected = 'Y'
                    ftp_connection.last_pwd_cached = self.password
                    break

    def close ( self ):
        #--------------

        print 'ftp/closing <' + self.host + '>'
        if ( self.host != 'localhost' ) :
            self.ftp.close()


    #reading the file allows a callback routine called for each line
    def get_ascii_file ( self, file_name, action_per_line ):
        #---------------------------------------------------

        print 'ftp/from <' + self.host + '>'
        print '_getting <' + file_name + '>'

        if ( self.host != 'localhost' ) :

            self.ftp.retrlines ( 'RETR ' + file_name, action_per_line )

        else:

            self.file = open ( file_name, 'r' )
            while ( 1 ):
                self.line = self.file.readline()
                if ( self.line == '' ) : break ;
                action_per_line ( self.line )
            self.file.close()


    def put_ascii_file ( self, ftp_dir_name,
                               ftp_file_name,
                               target_file ):
        #------------------------------------

        self.create_dir_if_needed ( ftp_dir_name[:-1] )  #remove trailing '/'

        print 'ftp/onto <' + self.host + '>'
        print '_putting <' + ftp_dir_name + ftp_file_name + '>'
#        print '_in ascii transfer mode'
        if ( self.host != 'localhost' ) :

            self.ftp.storlines ('STOR ' + ftp_dir_name
                                        + ftp_file_name,
                                target_file )
        else:

            self.target_file = open ( ftp_dir_name + ftp_file_name, 'w' )
            for  self.line in target_file.read () :
                self.target_file.write ( self.line )


    def put_binary_file ( self, ftp_dir_name,
                                ftp_file_name,
                                target_file ):
        #------------------------------------

        self.create_dir_if_needed ( ftp_dir_name[:-1] )  #remove trailing '/'

        print 'ftp/onto <' + self.host + '>'
        print '_putting <' + ftp_dir_name + ftp_file_name + '>'
#        print '_in binary transfer mode'
        if ( self.host != 'localhost' ) :

            self.ftp.storbinary ('STOR ' + ftp_dir_name
                                         + ftp_file_name,
                                 target_file,
                                 file_buffer_size )
        else:

            self.target_file = open ( ftp_dir_name + ftp_file_name, 'w' )
            for  self.line in target_file.read () :
                self.target_file.write ( self.line )


    def create_dir_if_needed ( self, ftp_dir_name ):
        #------------------------------------------

        self.split_dir_name = os.path.split ( ftp_dir_name )
        #print ftp_dir_name
        #print self.split_dir_name

        if ( self.host != 'localhost' ) :

            try: # nlst now crashes python 2.2 ftplib on empty directory

              self.ftp_nlst = self.ftp.nlst( self.split_dir_name[0] )
              #print self.ftp_nlst 

            except:

              self.ftp_nlst = []

            # previous ftp versions was (and the alphaNT server still is) listing just the file names 
            # but the dept ftp server now seems to list the relative path from home dir
            # so be ready to recognize the existence of the directory both ways
            if ( ( self.split_dir_name[1] not in self.ftp_nlst ) \
            and ( ftp_dir_name not in self.ftp_nlst ) ) :    

                if ( self.confirm_dir_creation == 'Y' ) :
                    print '.'
                    print 'Spin> Attention Please:'
                    print '.'
                    print '      Directory <' + ftp_dir_name + '>'
                    print '      Does not exist on <' + self.host + '>'
                    print '      Do you want to create this directory? '
                    print '.'
                    if ( string.lstrip( string.upper( raw_input( 'Spin Go Y/[N] : ' ) ) ) [:1] != 'Y' ):
                        print 'Spin> Aborting: No directory created'
                        Done()
                    else:
                        print '.'
                        print 'Spin> Ok, Proceding with spin request...'
                        print '.'

                # ftp.mkd cannot create nested directories at once,
                # do recursive call if needed
                if ( len ( self.ftp_nlst ) == 0 ) :
                    #print "recursive call ..."
                    self.create_dir_if_needed ( self.split_dir_name[0] )

                print 'ftp/creating <' + self.host + '>'
                print '_directory   <' + ftp_dir_name + '>'
                self.ftp.mkd ( ftp_dir_name )

        else:

            if ( self.split_dir_name[0][-2] != ':' ) :
                self.create_dir_if_needed ( self.split_dir_name[0] )
                self.split_dir_name = os.path.split ( ftp_dir_name ) # restore variable after recursive call

            print os.listdir ( self.split_dir_name[0] )
            if ( self.split_dir_name[1] not in os.listdir( self.split_dir_name[0] ) ) :
                print 'local/creating : ' + self.host
                print '_directory : ' + ftp_dir_name
                os.mkdir ( ftp_dir_name )


    def nlst ( self, ftp_path_name_or_options ): # used in generating fresh spin$map
        #------------------------------------------
        # issues a NLST command and return the list generated
        # the argument can be a path or option(s) for the 'ls' command on the remote host
        # in particular '-pLR' returns a recursive list of all the files.
        return  self.ftp.nlst( ftp_path_name_or_options )


    def cwd ( self, ftp_path_name ):
        #------------------------------------------
        self.ftp.cwd( ftp_path_name )



############################################################################
# parsing of the spin$map file -- low level single record parser
############################################################################

class spin_map_record_parser:
#============================
# check a spin$map record passed as a set of tokens
# for a target defined at object creation timw
# to match and record all the line information about that entry

    #these are the indices of each keyword on a spin$map line
    Kspin_map_column_file_name      = 0
    Kspin_map_column_file_dir       = 1
    Kspin_map_column_file_version   = 2
    Kspin_map_column_backup_updated = 3
    Kspin_map_column_fnal_updated   = 4
    Kspin_map_column_time_stamp     = 5
    Kspin_map_total_column          = 6

    Kspin_map_fill_width = [ 50, 90, 96, 98, 100, 110 ] # each field above is padded to these minimum column numbers

    def __init__ (self):
        #---------------
        self.found = 'N'
        self.file_name = ''
        self.file_dir = ''
        self.file_version = ''
        self.backup_updated = ''
        self.fnal_updated = ''
        self.time_stamp = ''
        self.at_rec_num = -1

    def look_here ( self, line_tokens, line_num ):
        #-----------------------------------------

#        print line_tokens

        # convert the spin$map file name token to lowercase
        # so that it can 'heal' itself if uppercase characters were entered by accident
        if ( string.lower( line_tokens[self.Kspin_map_column_file_name] ) == self.file_name ):
#            print ' found record for <' + self.file_name + '> at line #' + str(line_num)
            if ( self.found == 'Y' ) :
                print '.'
                print 'Spin> Attention Please:'
                print '.'
                print '     Multiple match found in ' + spin_map_name \
                        + ' for <' + self.file_name + '>'
                print '.'
                print 'Is the intended Target Directory <' + self.file_dir + '>'
                if ( string.lstrip( string.upper( raw_input( 'Y/[N] : ' ) ) ) [:1] == 'Y' ):
                    self.found = 'YY'   # remember that we already have our target

            if ( self.found == 'YY' ) : # we already have our target,
                    return              # so don't overwrite it

            self.found           = 'Y'
            self.line_tokens     = line_tokens
            self.file_dir        = string.lower ( line_tokens[self.Kspin_map_column_file_dir] )
            if ( self.file_dir[0] == '/' ) : # guarantee there is no leading slash
                self.file_dir        = self.file_dir[1:]
            if ( self.file_dir[-1] != '/' ) : # guarantee there is a trailing slash
                self.file_dir        = self.file_dir + '/'
            self.file_version    = line_tokens[self.Kspin_map_column_file_version]
            self.backup_updated  = line_tokens[self.Kspin_map_column_backup_updated]
            self.fnal_updated    = line_tokens[self.Kspin_map_column_fnal_updated]
            self.time_stamp      = line_tokens[self.Kspin_map_column_time_stamp]
            self.line_num        = line_num


    def increment_version ( self ):
        #-----------------------------------

        self.file_version = string.atoi ( self.file_version )
        self.file_version = self.file_version + 1
        self.file_version = '%4.4d' % self.file_version

        self.time_stamp      = time.strftime ( "%a-%d-%b-%Y-%X", # e.g. 'Wed-14-Jul-1999-00:24:23'
                                               time.localtime( time.time() ) )

        self.line_tokens[self.Kspin_map_column_file_version] = self.file_version
        self.line_tokens[self.Kspin_map_column_time_stamp]     = self.time_stamp


    def create_record ( self, target_dir, line_num ):
        #----------------------------------------------
        self.file_name       = string.lower ( self.file_name ) # last chance to force it lowercase
        self.file_dir        = string.lower ( target_dir )
        if ( self.file_dir[0] == '/' ) : # guarantee there is no leading slash
            self.file_dir        = self.file_dir[1:]
        if ( self.file_dir[-1] != '/' ) : # guarantee there is a trailing slash
            self.file_dir        = self.file_dir + '/'
        self.file_version    = '0000'
        self.backup_updated  = 'N'
        self.fnal_updated    = 'N'
        self.line_num        = line_num
        self.time_stamp      = time.strftime ( "%a-%d-%b-%Y-%X", # e.g. 'Wed-14-Jul-1999-00:24:23'
                                               time.localtime( time.time() ) )

#        self.line_tokens     = [ self.file_name,
#                                 self.file_dir,
#                                 self.file_version,
#                                 self.backup_updated,
#                                 self.fnal_updated,
#                                 self.time_stamp ]

#        replace the above line with something that automatically tracks
#        the order of the columns as defined in the self.Kspin_map_*** constants

        self.line_tokens = []
        for  self.item  in  range (self.Kspin_map_total_column) :
            self.line_tokens.append ( '' )

        self.line_tokens[self.Kspin_map_column_file_name]        = self.file_name
        self.line_tokens[self.Kspin_map_column_file_dir]         = self.file_dir
        self.line_tokens[self.Kspin_map_column_file_version]     = self.file_version
        self.line_tokens[self.Kspin_map_column_backup_updated]   = self.backup_updated
        self.line_tokens[self.Kspin_map_column_fnal_updated]     = self.fnal_updated
        self.line_tokens[self.Kspin_map_column_time_stamp]       = self.time_stamp


    def formatted_line ( self ):
        #---------------------

        self.line = ''

        for  self.item  in  range (self.Kspin_map_total_column) :

            self.line = self.line + self.line_tokens[self.item]
            self.line = self.line + max ( 1, ( self.Kspin_map_fill_width[self.item]-len(self.line) ) ) * ' '

#        print self.line
        return self.line

    def print_result ( self ):
        #---------------------

        if ( self.found == 'N' ):

            print ' record for <' + self.file_name \
                + '> not found in ' + spin_map_name

        else:

            print ' record found in ' + spin_map_name \
                + ' for <' + self.file_name + '>'
#            print '   at line #                 ' + str(self.line_num)
#            print '   target directory is       ' + self.file_dir
#            print '   current file version is   ' + self.file_version
#            print '   current backup status is  ' + self.backup_updated
#            print '   current fnal status is    ' + self.fnal_updated
#            print '   last spin date stamp is   ' + self.time_stamp




############################################################################
# parsing of the spin$map file -- low level single record parser
############################################################################

class spin_map_file_parser:
#==========================
# implements the callback routine used to test each line of the spin$map file
# to look for an entry for the desired target file,
# and also an entry for the spin$map itself,
# and an entry for this script

    def __init__ ( self, target_file_name ):
        #-----------------------------------
        self.spin_map_rec = []
        self.line_num = 0

        # we will be looking for a record matching the spin$map itself ...
        self.record_for_spin_map = spin_map_record_parser()
        self.record_for_spin_map.file_name = spin_map_name

        #... and one for this script
        self.record_for_spin_script = spin_map_record_parser()
        self.record_for_spin_script.file_name = spin_script_name

        #... and finally the file we are explicitely supposed to deal with
        self.record_for_target_file = spin_map_record_parser()
        self.record_for_target_file.file_name = string.lower ( target_file_name )

    def parse_one_line ( self, line ):
        #-----------------------------

        self.line_num = self.line_num + 1

#        print ' line #' + str(self.line_num) + ' : ' + line

        line = string.rstrip ( line ) # drop trailing spaces

        # keep a record of all lines in the file so that it can be updated
        self.spin_map_rec.append ( line )

        if ( len(line) == 0 ) :
#            print 'Spin> Info: skipping blank line at line #'+ str(self.line_num)
            return      # skip blank lines

        if ( ( line[0] == '#' ) or ( line[0] == '!' ) ) :
#            print 'Spin> Info: skipping comment at line #'+ str(self.line_num)
#            print '_Skipping : ' + line
            return         # skip comment lines

        # generate a new record with one item for each word on this line
        self.tokens = string.split ( line )
#        print self.tokens

        if ( len( self.tokens ) != spin_map_record_parser.Kspin_map_total_column ):
            print 'Spin> Warning: unexpected number of tokens at line # ' + str(self.line_num)
            print '_Skipping : ' + line[:-1]
            print '_Parsed as : ' + str(self.tokens)

        else:
            self.record_for_spin_map.look_here    ( self.tokens, self.line_num )
            self.record_for_spin_script.look_here ( self.tokens, self.line_num )
            self.record_for_target_file.look_here ( self.tokens, self.line_num )

    def increment_spin_map_version ( self ):
        #-----------------------------------
        self.record_for_spin_map.increment_version ()
        self.spin_map_rec[self.record_for_spin_map.line_num-1] = self.record_for_spin_map.formatted_line()


    def increment_spin_script_version ( self ):
        #-----------------------------------
        self.record_for_spin_script.increment_version ()
        self.spin_map_rec[self.record_for_spin_script.line_num-1] = self.record_for_spin_script.formatted_line()


    def increment_target_file_version ( self ):
        #-----------------------------------
        self.record_for_target_file.increment_version ()
        self.spin_map_rec[self.record_for_target_file.line_num-1] = self.record_for_target_file.formatted_line()


    def create_target_file_record ( self, target_dir ):
        #----------------------------------------------
        self.line_num = self.line_num + 1
        self.record_for_target_file.create_record ( target_dir, self.line_num )
        self.spin_map_rec.append ( self.record_for_target_file.formatted_line() )


    def print_result ( self ):
        #---------------------
        print '.'
        print ' Done parsing ' + spin_map_name

        self.record_for_spin_map.print_result ()
        self.record_for_spin_script.print_result ()
        self.record_for_target_file.print_result ()

#        print '.'
#        print 'Dump of ' + spin_map_name + ' :'
#        for  self.line_num  in  range(len(self.spin_map_rec)) :
#            print self.spin_map_rec[self.line_num]



############################################################################
# find the last modified file in the current local directory
############################################################################

def find_last_modified( dir, dir_list ):
#------------------------
# locate the most recently updated file

    Kindex_modified_time = 8

    latest_file_name = ''
    latest_file_time = 0

    for  file_name  in  dir_list :
        file_stats = os.stat( dir + file_name )

        if ( file_stats[Kindex_modified_time] > latest_file_time ) :
            latest_file_name = file_name
            latest_file_time = file_stats[Kindex_modified_time]

    return latest_file_name



############################################################################
# close all possibly opened files
# Make exit actions a function so that we can use it for aborting from anywhere
############################################################################

def Done():
#----------

    print '.'

    if ( globals().has_key( 'home_ftp_access' ) ) :
        home_ftp_access.close ()

    if ( globals().has_key( 'archive_ftp_access' ) ) :
        archive_ftp_access.close ()

    if ( globals().has_key( 'target_file_access' ) ) :
        target_file_access.close ()

    if ( globals().has_key( 'temp_spin_map_file' ) ) :
        temp_spin_map_file.close ()

    if ( globals().has_key( 'new_spin_map_file' ) ) :
        new_spin_map_file.close ()

    print '.'
    print 'Done.'

    if ( globals().has_key( 'wait_on_exit' ) ) : raw_input ( '<CR>' )

    sys.exit()

#////////////////////////////////////////////////////////////////////////

def Spin_One_File ( target_file = '', file_transfer_mode = '', force_new_entry = '' ) :
    #-----------------

    # parse specified file to extract file and directory names
    #---------------------------------------------------------
    target_file_split = os.path.split ( target_file )
    target_file_name  = target_file_split[1]
    target_file_dir   = target_file_split[0]
    if ( target_file_dir == '' ) : target_file_dir = '.'
    target_file_dir = target_file_dir + '/'
    target_file = target_file_dir + target_file_name

#    print ' target_file      = ' + target_file
#    print ' target_file_dir  = ' + target_file_dir
#    print ' target_file_name = ' + target_file_name

    # get a listing of the apropriate directory
    #------------------------------------------
    target_file_dir_list = os.listdir( target_file_dir )
#    print ' target_file_dir_list = ', target_file_dir_list

    #find target file we are supposed to operate on
    #----------------------------------------------
    if ( target_file_name == '' ) :
        print '.'
        print 'Which file are we going to spin ? '
        last_modified = find_last_modified( target_file_dir, target_file_dir_list )
        target_file_name = raw_input ( 'Enter File Name or <CR> for [' + last_modified + '] : ' )
        if ( string.strip( target_file_name ) == '' ) :
            target_file_name = last_modified
        else : # look to see if a new path name was specified
            target_file_split_new = os.path.split ( target_file_name )
            target_file_name  = target_file_split_new[1]
            if ( target_file_split_new[0] != '' ) :
                target_file_dir      = target_file_split_new[0] + '/'  # replace directory name
                target_file_dir_list = os.listdir( target_file_dir )   # redo directory listing
                target_file_split    = target_file_split_new           # update that too, while not currently re-used
        target_file = target_file_dir + target_file_name

    #check for file existence
    #------------------------
    if ( target_file_name   not in  target_file_dir_list ) :
        print '.'
        print 'Spin> Error: Could not locate file <' + target_file_name + '>'
        Done()

    #check for convention of lowercase only
    #--------------------------------------
    if ( string.lower( target_file_name ) != target_file_name ) :
        print '.'
        print 'Spin> Warning: By convention we only use lowercase letters in file names.'
        print '              All files on the FTP sites have lowercase file names.'
        print '              Your file name will be converted to lowercase during transfer.'


    #look at file extension to guess if ascii or binary transfer mode is apropriate
    #----------------------
    if ( file_transfer_mode == '' ) :
        dot_index = string.rfind ( target_file_name, '.' )
        target_file_extension = ''
        if ( dot_index >= 0 ) :
            target_file_extension = string.lower( target_file_name[dot_index:] )
    #        print ' target_file_extension = ', target_file_extension

            if ( ( target_file_extension == '.gif' )
              or ( target_file_extension == '.jpg' ) 
              or ( target_file_extension == '.bmp' ) 
              or ( target_file_extension == '.pdf' ) 
              or ( target_file_extension == '.xls' ) 
              or ( target_file_extension == '.tar' ) 
              or ( target_file_extension == '.gz' ) 
              or ( target_file_extension == '.zip' ) ) :
                file_transfer_mode = 'binary'
            else :
                file_transfer_mode = 'ascii'

#    print ' file_transfer_mode = ', file_transfer_mode


    #open connection to home ftp site
    #--------------------------------
    print '.'
    print 'Connecting to Home FTP Server'
    home_ftp_access = ftp_connection()
    home_ftp_access.open ( home_ftp_ip_address, home_ftp_user )

    if ( home_ftp_access.connected != 'Y' ) : Done () #Abort

    #open connection to Archival ftp site
    #--------------------------------
    print '.'
    print 'Connecting to Archival FTP Server'
    archive_ftp_access = ftp_connection()
    archive_ftp_access.open ( archive_ftp_ip_address, archive_ftp_user )

    if ( archive_ftp_access.connected != 'Y' ) : Done () #Abort

    #read and parse spin$map
    #-----------------------
    print '.'
    parsed_spin_map = spin_map_file_parser ( target_file_name )
    home_ftp_access.get_ascii_file ( home_ftp_head_dir + spin_map_dir + spin_map_name,
                                     parsed_spin_map.parse_one_line )

    #print success/failure finding the target records
    #---------------------
#    parsed_spin_map.print_result()

    if ( parsed_spin_map.record_for_spin_map.found == 'N' ) :
        print '.'
        print 'Spin> Fatal Error: Record for <' + spin_map_name \
                                                + '> must be present in the ' + spin_map_name + ' File'
        Done()

    if ( parsed_spin_map.record_for_spin_script.found == 'N' ) :
        print '.'
        print 'Spin> Fatal Error: Record for <' + spin_script_name \
                                                + '> must be present in the ' + spin_map_name + ' File'
        Done()

    #compare the version number of the script recorded in spin$map
    #-------------------------------------------------------------
    if ( parsed_spin_map.record_for_spin_script.file_version > spin_script_version ):
        print '.'
        print 'Spin> Attention Please:'
        print '.'
        print '      There is a newer spin command script on our ftp site. '
        print '      You probably should update to the most recent version. '
        print '      This spin script file thinks it is version : <' + spin_script_version + '>'
        print '      The spin$map thinks the current version is : <' + parsed_spin_map.record_for_spin_script.file_version + '>'
        print '.'
        if ( string.lstrip( string.upper( raw_input( 'Spin Abort [Y]/N : ' ) ) ) [:1] != 'N' ):
            print 'Spin> Aborting: use your web browser to get the current version from'
            print '     http://' + home_http_ip_address + '/' + home_http_head_dir \
                      + parsed_spin_map.record_for_spin_script.file_dir \
                      + parsed_spin_map.record_for_spin_script.file_name
            Done()
        else:
            print '.'
            print 'Spin> Ok, Proceding with spin request...'


    #check if it is the spin script itself we are updating
    #--------------------------------------
    if ( string.lower( target_file_name ) == spin_script_name ) :

        # read in the source file (i.e. this script)
        target_file = open ( target_file, 'r' )
        source_records = target_file.readlines ()
        target_file.close ()

        parsed_spin_map.increment_spin_script_version ( )

        # create a new target file name for the updated script
        # and change the target file name
        target_file_name = target_file_name + '.' + parsed_spin_map.record_for_spin_script.file_version
        target_file = target_file_dir + target_file_name

        print '.'
        print 'Spin> Warning: Spin noticed the target file is the spin script itself.'
        print '              Spin needs to Update the Version Number inside the source file.'
        print '              The New Version Number will be <' + parsed_spin_map.record_for_spin_script.file_version + '>'
        print '              Spin will Create a New Local File <' + target_file + '>'
        print '              You can Delete or Rename this Local File when we are all done.'

        target_file_access = open ( target_file, 'w' )

        # update the first line of the spin script...
        target_file_access.write ( 'spin_script_version = "%s" \n' % parsed_spin_map.record_for_spin_script.file_version )
        # ...and just copy the rest of the file over
        target_file_access.writelines ( source_records[1:] )

        target_file_access.close ( )


    #If the file isn't already known in spin$map
    #then we need to create a new entry
    #-----------------------------------
    if ( parsed_spin_map.record_for_target_file.found[0] != 'Y' ) :

        print '.'
        print 'Spin> Attention Please: '
        print '.'
        print '     Could not find an entry for <' + target_file_name \
                    + '> in ' + spin_map_name
        print '     Would you like to create a new Entry?'
        print '.'

        if ( string.lstrip( string.upper( raw_input( 'Spin New Entry [Y]/N : ' ) ) ) [:1] == 'N' ):
            print 'Ok, Spin Aborting.'
            Done()

    if ( ( parsed_spin_map.record_for_target_file.found[0] != 'Y' )
      or ( force_new_entry == 'yes' ) ) :

        print '.'
        print '     What is the Desired Target Directory for <' + target_file_name + '> '
        print '     Note: if it is NOT an HTML document, it should probably start with ftp/'
        print '     Example: <ftp/l1/framework/>'
        print '.'

        target_dir = string.lower( raw_input( 'Enter Target Directory : ' ) )

        # clean up directory name
        target_dir = string.strip ( target_dir )
        target_dir = string.lower( target_dir )

        if ( ( target_dir == '' ) or
             ( string.find ( target_dir, ' ' ) >= 0 )
          or ( string.find ( target_dir, chr(9) ) >=  0 ) ) :
            print 'No Tab or Space allowed in target directory.'
            Done()

        parsed_spin_map.create_target_file_record ( target_dir )

    #We have all the information; ready to go
    #----------------------------------------
    print '.'
    print 'Spin> Confirmation Please:'
    print '.'
    print '  Ready to Update         : ' + target_file
    print '  On FTP Server           : ' + home_ftp_ip_address
    print '  using ftp Transfer Mode : ' + file_transfer_mode
    print '  To Directory            : ' + home_ftp_head_dir + parsed_spin_map.record_for_target_file.file_dir
    print '  To File Name            : ' + parsed_spin_map.record_for_target_file.file_name
    print '  Last Registered Version : ' + parsed_spin_map.record_for_target_file.file_version
    print '  Last Registered on      : ' + parsed_spin_map.record_for_target_file.time_stamp
    print '  WWW Access will be on   : ' + 'http://' + home_http_ip_address
    print '  with File Name          : ' + '/' + home_http_head_dir + parsed_spin_map.record_for_target_file.file_dir + parsed_spin_map.record_for_target_file.file_name
    print '.'

    if ( string.lstrip( string.upper( raw_input( 'Spin Go [Y]/N : ' ) ) ) [:1] == 'N' ):
        print 'Ok, Spin Aborting.'
        Done()

    #Now open the file to transfer
    #-----------------------------

    if ( file_transfer_mode == 'ascii' ) :
        target_file_access = open ( target_file, 'r' )
    else :
        # add the 'b' tag to the mode to tell the system it is a binary file (important on some systems)
        # and specify a file buffer size that will be used in ftplib.storbinary (this may not be critical)
        target_file_access = open ( target_file, 'rb', file_buffer_size )

    # Send the Target file to the Home FTP Site
    #------------------------------------------
    print '.'
    print ' Updating Home FTP Server'
    if ( file_transfer_mode == 'ascii' ) :
        home_ftp_access.put_ascii_file    ( home_ftp_head_dir + parsed_spin_map.record_for_target_file.file_dir,
                                            parsed_spin_map.record_for_target_file.file_name,
                                            target_file_access )
    else :
        home_ftp_access.put_binary_file   ( home_ftp_head_dir + parsed_spin_map.record_for_target_file.file_dir,
                                            parsed_spin_map.record_for_target_file.file_name,
                                            target_file_access )

    # Send the Target file to the Archival FTP Site
    #----------------------------------------------
    parsed_spin_map.increment_target_file_version ()

    #reset the file position to the beginning of the file
    target_file_access.seek ( 0 )

    print '.'
    print ' Updating Archival FTP Server'
    archive_ftp_access.confirm_dir_creation = 'N'  # create directories as needed without asking
    if ( file_transfer_mode == 'ascii' ) :
        archive_ftp_access.put_ascii_file  ( archive_ftp_head_dir + parsed_spin_map.record_for_target_file.file_dir,
                                             parsed_spin_map.record_for_target_file.file_name + '.' + parsed_spin_map.record_for_target_file.file_version,
                                             target_file_access )
    else :
        archive_ftp_access.put_binary_file ( archive_ftp_head_dir + parsed_spin_map.record_for_target_file.file_dir,
                                             parsed_spin_map.record_for_target_file.file_name + '.' + parsed_spin_map.record_for_target_file.file_version,
                                             target_file_access )



    # Now send the updated spin$map
    #------------------------------
    if ( string.lower( target_file_name ) == spin_map_name ) : # all done if target file is spin$map
        return  # otherwise we would be overwriting the new spin$map with a modified old one

    parsed_spin_map.increment_spin_map_version ()

    print '.'
    print ' Now Updating the ' + spin_map_name

    # we need to make a temporary local file for the NEW spin map
    temp_spin_map_name = tempfile.mktemp()
#    print  ' temp_spin_map_name = ' + temp_spin_map_name

    temp_spin_map_file = open ( temp_spin_map_name, 'w' )

    for  spin_map_line  in  parsed_spin_map.spin_map_rec  :
    #    print spin_map_line
        temp_spin_map_file.write ( spin_map_line + '\n' )

    temp_spin_map_file.close ( )
    temp_spin_map_file = open ( temp_spin_map_name, 'r' )

    home_ftp_access.put_ascii_file    ( home_ftp_head_dir + spin_map_dir,
                                        spin_map_name,
                                        temp_spin_map_file )

    #reset the file position to the beginning of the file
    temp_spin_map_file.seek ( 0 )

    archive_ftp_access.put_ascii_file ( archive_ftp_head_dir + spin_map_dir,
                                        spin_map_name + '.' + parsed_spin_map.record_for_spin_map.file_version,
                                        temp_spin_map_file )


    # delete the temporary file
    temp_spin_map_file.close ()
    os.remove ( temp_spin_map_name )

#\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
#////////////////////////////////////////////////////////////////////////
#\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\

def Spin_Generate_Map () :
    #---------------------

    #open connection to home ftp site
    #--------------------------------
    print '.'
    print 'Connecting to Home FTP Server'
    home_ftp_access = ftp_connection()
    home_ftp_access.open ( home_ftp_ip_address, home_ftp_user )

    #open connection to Archival ftp site
    #--------------------------------
    if ( 0 ) : # not yet needed, but will be to retrieve latest version number
        print '.'
        print 'Connecting to Archival FTP Server'
        archive_ftp_access = ftp_connection()
        archive_ftp_access.open ( archive_ftp_ip_address, archive_ftp_user )

    #retrieve a recursive list of all files
    # -p       Put a slash (/) after each filename if the file is a directory.
    # -L       If an argument is a symbolic link, list the file or directory
    #          the link references rather than the link itself.
    # -R       Recursively list subdirectories encountered.
    #-----------------------
    print '.'
    home_ftp_access.cwd ( home_ftp_head_dir )
    recursive_file_list = home_ftp_access.nlst ( '-pLR' )
    #import test_nlst
    #recursive_file_list = test_nlst.test_nlst


    #open a new file for the new spin$map
    #------------------------------------
    new_spin_map_file = open ( spin_map_name, 'w' )

    new_spin_map_file.write ( "!New Spin Map Generated "
                            + time.asctime ( time.localtime( time.time() ) )
                            + '\n' )

    #we are going use the record parser object
    #in particular record creation and line formatting
    #-------------------------------
    spin_map_record = spin_map_record_parser ()
    file_num = 0

    #scan through each item in the list of files
    # example of list returned by nlst ( '-pLR' )
    #    ['.:', 'd0_logo_bw.gif', 'd0_logo_small.gif', 'ftp/', 'index.html', 'l1/', 'l2/'
    #    , 'msu_d0_people.html', 'run1/', 'test.html', 'trigger.html', '', './ftp:', 'l1/',
    #    'l2/', 'run1/', 'scl/', 'spin/', 'tcc/', '', './ftp/l1:', 'cal_trig/', 'framework/', '',...
    #-------------------------------------------
    for  item    in    recursive_file_list  :

        if ( item == ''  ) : continue  # skip blank records before starting new sub dir lists

        if ( item[-1] == '/' ) : continue # skip, this is the name of a subdirectory within a dir

        if ( item[-1] == ':' ) : # new sub directory listing starting; maybe true for Solaris' Ftp only
            file_dir = item[2:-1] + '/' # drop trailing colon and add a trailing slash
            if ( file_dir == '/' ) : file_dir = './' # fixup the base directory
            continue

        if ( file_dir[:2] == 'l2' ) :                         # skip L2 files ...
            if ( file_dir[:12] != 'l2/framework' ) : continue # ... except L2 FW files
        if ( file_dir[:6] == 'ftp/l2' ) :
            if ( file_dir[:16] != 'ftp/l2/framework' ) : continue

        file_num = file_num + 1
        spin_map_record.file_name = item

        spin_map_record.create_record ( file_dir, file_num )
        new_spin_map_file.write ( spin_map_record.formatted_line() + '\n' )

#        raw_input( '<CR>' )


    new_spin_map_file.write ( "!Total of " + str(file_num)
                            + " Files Automatically Recorded in Spin Map File"
                            + '\n' )

    print str(file_num) + ' files found'
    print 'A New <' + spin_map_name + '> File has been created locally'
    print 'Please review this file and, for example, use Spin to update this file'


#\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
#////////////////////////////////////////////////////////////////////////
#\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
#                 dispatch to the proper function call
#\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
#////////////////////////////////////////////////////////////////////////
#\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\

# It is simple if there were no command line argument 

if ( len (sys.argv) <= 1 ) :

    Spin_One_File ( )
    Done()


# read and parse command line arguments

command_line_argument = sys.argv[1:] 


if ( command_line_argument[0] == "-generate_map" ) :

    print '           Spin Map File Generator'
    print '                -------------'
    print '.'
    print '(Note: Tested with Home Ftp Site on Solaris Only)'

    # this makes only sense on the real ftp site
    if ( ( home_ftp_ip_address != 'www.pa.msu.edu' )         # Official Home
      or ( home_ftp_head_dir   != 'www/' ) ) :               # link to DZero Web area
        print 'Command only valid for home location = www.pa.msu.edu/www'
        print 'Overriding the location variables'
        home_ftp_ip_address = 'www.pa.msu.edu'
        home_ftp_head_dir   = 'www/'

    Spin_Generate_Map ()



elif ( ( command_line_argument[0] == "-doc" )
    or ( command_line_argument[0] == "-d" ) ):

    Spin_Doc ()



elif ( ( command_line_argument[0] == "-help" )
    or ( command_line_argument[0] == "-h" )
    or ( command_line_argument[0] == "-?" )
    or ( command_line_argument[0] == "?" ) ) :

    Spin_Help ()



elif ( ( command_line_argument[0] == "-binary" )
    or ( command_line_argument[0] == "-b" )

    or ( command_line_argument[0] == "-ascii" )
    or ( command_line_argument[0] == "-a" )

    or ( command_line_argument[0] == "-new" )
    or ( command_line_argument[0] == "-n" )

    or ( command_line_argument[0] == "-archive_node" )
    or ( command_line_argument[0] == "-rn" )

    or ( command_line_argument[0] == "-archive_dir" )
    or ( command_line_argument[0] == "-rd" )

    or ( command_line_argument[0][0:1] != "-" ) )  : # no command line option


    file_transfer_mode = ''
    force_new_entry = ''
    target_file = ''

    i = 0 # build explicit do loop (instead of "for i in range...") to allow "i=i+1"
    while ( i < len(command_line_argument) ) :

        # look for an explicit transfer mode
        if   ( ( command_line_argument[i] == "-binary" )
            or ( command_line_argument[i] == "-b" ) )  :
            file_transfer_mode = 'binary'

        elif ( ( command_line_argument[i] == "-ascii" )
            or ( command_line_argument[i] == "-a" ) )  :
            file_transfer_mode = 'ascii'

        # look for a new entry request
        elif ( ( command_line_argument[i] == "-new" )
            or ( command_line_argument[i] == "-n" ) )  :
            force_new_entry = 'yes'

        # look for a new archive node
        elif ( ( command_line_argument[i] == "-archive_node" )
            or ( command_line_argument[i] == "-rn" ) )  :
            try : 
                i=i+1 
                archive_ftp_ip_address = command_line_argument[i] 
            except :
                print ' ** Could not find command line argument for archive node name ** '
                Spin_Help ()
                Done()

        # look for a new archive directory
        elif ( ( command_line_argument[i] == "-archive_dir" )
            or ( command_line_argument[i] == "-rd" ) )  :
            try : 
                i=i+1 
                archive_ftp_head_dir   = command_line_argument[i] 
                if ( archive_ftp_head_dir[-1:] != '/' ) : 
                    archive_ftp_head_dir = archive_ftp_head_dir + '/' 
            except :
                print ' ** Could not find command line argument for archive directory name ** '
                Spin_Help ()
                Done()

        # look for an explicit file name
        elif ( command_line_argument[i][0:1] != '-' ) :
            if ( len (sys.argv) > 1 ) : 
                target_file = command_line_argument[i]

        # switch to next argument
        i=i+1 

    Spin_One_File ( target_file, file_transfer_mode, force_new_entry )


else : # catch all other illegal options

    Spin_Help ()


#Cleanup
#-------
Done()

