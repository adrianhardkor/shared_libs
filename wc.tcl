proc set_debug {num} {
  switch -- $num {
    "0" {log_user 0;}
    "1" {log_user 1;}
    "2" {
      exp_internal 1;
    }
  }
}

# START SCRIPT TIMER
global timer
set timer(SCRIPT,def) "milliseconds"
set timer(SCRIPT) [clock $timer(SCRIPT,def)]

proc timer_index_since {index} {
  global timer
  switch -- $timer($index) {
    {} {return -1}
    default {return [expr [clock $timer($index,def)] - $timer($index)]}
  } 
}

proc mcsplit "str splitStr {mc {\x00}}" {
    return [split [string map [list $splitStr $mc] $str] $mc]
}

proc argv_array {} {
  global argv_array
  array unset argv_array
  global argv
  foreach  {i v} $argv {
    set argv_array([string trimleft $i "-"])  [split $v "=,"] 
  }
  for i [array names argv_array] {
    puts "$i\t$argv_array($i)"
  }
}

proc echo_param {paired_list} {
  array set pl $paired_list
  # get colum-len
  set maxlen 0
  foreach il [array names pl] {
    set thislen [string length $il]
    if {$thislen > $maxlen} {set maxlen $thislen}
  }
  set maxlen [expr 5+$maxlen]
  set header "=============================="
  puts $header
  foreach index [lsort -dictionary [array names pl]] {
    puts -nonewline "[format "%-*s" $maxlen $index]\="
    if {$index == ""} {puts "\n"}
    foreach line [split $pl($index) "\n"] {puts "  $line"}
  }
  puts $header
}

proc clrinbuff {} {
  global spawn_id
   expect {
      -re {.*$} { }
   }
}

proc mrvTS_exit {} {
  global spawn_id mrv0 mrv15 send_slow
  send -s -- "\x1A";
  expect -- "exit";
  send -- "e\r";
  after 450

  # back to TS
  send -s -- "exit\r";
  append output $expect_out(buffer)
  expect -re $mrv15 {send -s -- "exit\r";}
  append output $expect_out(buffer)
  expect -re $mrv0 {send -s -- "exit\r";}
  append output $expect_out(buffer)
  expect "isconnect"
  # spawn_id dead
}

proc mrvTS_show {ts_ip ts_user ts_pass1 ts_pass2 ts_port} {
   puts "MRVTS_SHOW_PORTS_START"
   log_user 0
   set timeout 30
   set commands [list "no pause" "show port async summary" "" "exit"]
   # no pause
   # show port async summary
  global spawn_id mrv0 mrv15 send_slow
  set mrv0 {([:]+[0-9\ ]+[>])}
  if {[catch {spawn ssh -l $ts_user $ts_ip} err2]} {
    puts "SSH Failure"
    exit 5
  } else {
    # show port async summary
    after 1100
    set send_slow {1 .01}
    set each 0
    set cIndex 0
    while {$each <= 20} {
      expect {
        -re $mrv0 {
          append output $expect_out(buffer)
          # logged-in
          send -s -- "[lindex $commands $cIndex]\r";
          set cIndex [expr $cIndex + 1]
          if {$cIndex > [llength $commands]} {break}
        }
        "s password: " {
          append output $expect_out(buffer)
          # priv0 password
          clrinbuff
          send -s -- "$ts_pass1\r";
          after 500
        }
        "Password" {
          append output $expect_out(buffer)
          # priv15 password
          clrinbuff
          send -s -- "$ts_pass2\r";
        }
        "isconnec" {
            append output $expect_out(buffer)
            log_user 1
            puts "MRVTS_SHOW_PORTS_END"
            return $output
        }
        "re you sure you want to continue connectin" {send -- "yes\r";}
      }
      stty echo
      sleep 1
      incr each
    }
    log_user 1
    puts "MRVTS_SHOW_PORTS_END"
    return $output
  }
}

proc mrvTS {ts_ip ts_user ts_pass1 ts_pass2 ts_port {timeout 120}} {
  global spawn_id mrv0 mrv15 send_slow
  set mrv0 {([:]+[0-9\ ]+[>])}
  set mrv15 {>>}
  if {[catch {spawn ssh -l $ts_user $ts_ip} err2]} {
    puts "SSH Failure"
    exit 5
  } else {
    # show port async summary
    after 1100
    set send_slow {1 .01}
    set each 0
    while {$each <= 20} {
      expect {
        -re $mrv15 {
          # LOGGED IN -- CONNECT PORT
          append output $expect_out(buffer)
          after 500
          send -s -- "connect port async $ts_port \r";
          after 2000
          expect -re ".*" {send -s -- "\r\r\r";}
          after 1750
          break
        }
        -re $mrv0 {
          append output $expect_out(buffer)
          # logged-in
          send -s -- "enable\r";
        }
        "isconnec" {
            return $output
        }
        "s password: " {
          append output $expect_out(buffer)
          # priv0 password
          clrinbuff
          send -s -- "$ts_pass1\r";
          after 500
        }
        "Password" {
          append output $expect_out(buffer)
          # priv15 password
          clrinbuff
          send -s -- "$ts_pass2\r";
        }
        "re you sure you want to continue connectin" {send -- "yes\r";}
      }
      stty echo
      sleep 1
      incr each
    }
    # TS portion complete
    set each 0
    while {$each <= 20} {
      expect {
         "mcc" {
          # JUNIPER
          puts "\n\nBAREMETAL: MRV_MCC"
          append output $expect_out(buffer)
          break;
        }
        "ogin: " {
          # JUNIPER
          puts "\n\nBAREMETAL: JUNIPER"
          append output $expect_out(buffer)
          break;
        }
        "FreeBSD" {
          puts "\n\nBAREMETAL:  bsd/linux"
          append output $expect_out(buffer)
          break;
        }
        "root@" {
          puts "\n\nBAREMETAL:  root/linux"
          append output $expect_out(buffer)
          break;
        }
        -re  "OTHER" {
          puts "\n\nBAREMETAL: OTHER"
          append output $expect_out(buffer)
          break
        }
        timeout {
          puts "\n\nBAREMETAL: EMPTY? -- $expect_out(buffer)"
          break
        }
      }
    }
    catch { mrvTS_exit }
  }
  return $output
}

proc parray_slow {array_name {outputme 1}} {
  set result {}
  upvar $array_name array_data
  set maxlen 0
  foreach index [array names array_data] {
    set thislen [string length $index]
    if {$thislen > $maxlen} {
      set maxlen $thislen
    }
  }
  set maxlen [expr 3+[string length $array_name]+$maxlen]
  foreach index [lsort -dictionary [array names array_data]] {
    if {$outputme == 1} {
      puts -nonewline "[format "%-*s" $maxlen ${array_name}($index)]\="
    }
    append result "[format "%-*s" $maxlen ${array_name}($index)]\="
    if {$array_data($index) == ""} {
      if {$outputme == 1} {puts "\n"}
      append result "\n"
      after 2;
    } else {
      foreach line [split $array_data($index) "\n"] {
        if {$outputme == 1} {puts "  $line\n"}
        append result "  $line\n"
        after 2;
      }
      after 1;
    }
  }
  return $result
}

global tcl_platform
echo_param [list \
  "Library" [info script] \
  "Hostname" [exec hostname] \
  "whoami" [exec whoami] \
  "nameofexe" [info nameofexe] \
  "pid" [pid] \
  "timestamp" [clock format [clock seconds] -format {%a, %b %d %Y | %T %Z}] \
  "InitTime" "[timer_index_since SCRIPT] $timer(SCRIPT,def)" \
  "tcl_platform_machine" $tcl_platform(machine) \
  "tcl_platform_os" $tcl_platform(os) \
  "tcl_platform_osVersion" $tcl_platform(osVersion) \
  "tcl_platform_platform" $tcl_platform(platform)]

argv_array

