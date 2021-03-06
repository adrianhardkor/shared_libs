proc set_debug {num} {
  switch -- $num {
    "0" {log_user 0;}
    "1" {log_user 1;}
    "2" {
      exp_internal 1;
    }
  }
}


proc timer_index_start {index {definition seconds}} {
    # 1st snapshot timer
    global timer_start
    set timer_start($index,definition) $definition
    set timer_start($index) [clock $definition]
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

proc grep {expression data} {
  set result {}
  foreach line [split $data "\n"] {
    if {[regexp -- $expression $line]} {
      lappend result $line
    }
  }
  return [join $result "\n"]
}

proc cleanLine {line} {
  return [lunique [split $line "\t "]]
}

proc lunique {input_list} {
  set result {}
  foreach element $input_list {
    if {[lsearch -exact $result $element]==-1} {
      lappend result $element
    }
  }
  return $result
}

# mrvTS_getports $argv_array(lx_ip) $cred(LX,user) $cred(LX,pass) $cred(LX,pass15) $argv_array(lx_port)
proc mrvTS_getports {lx_ip user pass pass15 lx_port} {
  set result [list]
  if {![is_pingable $lx_ip]} {puts "${lx_ip} NOT PINGABLE"; exit 5}
  if {$lx_port == 0} {
    foreach line [split [mrvTS_show $lx_ip $user $pass $pass15 ""] "\r\n"] {
        set poten [lindex [cleanLine $line] 1]
        if {[string is integer $poten] && $poten != ""} {
          lappend result [lindex [cleanLine $line] 1]
        }
    }
    puts $result
    return $result
  } else {
    return [list $lx_port]
  }
}

proc argv_array_run {} {
  global argv_array
  array unset argv_array
  global argv
  foreach  {i v} $argv {
    set argv_array([string trimleft [string trim $i] "-"])  [split [string trim $v] "="]
    # puts "[string trimleft $i "-"]\t[split $v "="]"
  }
  # echo_param [array get argv_array]
}

proc cred_array {varName} {
  upvar 1 $varName argv_array_inside
  global cred
  array unset cred
  foreach type $argv_array_inside(User_Pass_Json) {
    set type [split $type ",/"]
    set device [string trim [lindex $type 0]]
    switch -- [llength $type] {
      3 {
        set cred($device,user) [lindex $type 1]
        set cred($device,pass) [lindex $type 2]
      }
      4 {
        set cred($device,user) [lindex $type 1]
        set cred($device,pass) [lindex $type 2]
        set cred($device,pass15) [lindex $type 3]
      }
    }
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
    foreach line [split $pl($index) "\n"] {puts "  '$line'"}
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
  log_user 0
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
   set timeout 30
   set commands [list "no pause" "show port async summary" "" "exit"]
   # no pause
   # show port async summary
  global spawn_id mrv0 mrv15 send_slow
  set mrv0 {([:]+[0-9\ ]+[>])}
  if {[catch {spawn ssh -l $ts_user $ts_ip} err2]} {
    puts "SSH Failure: $err2"
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
            return $output
        }
        "re you sure you want to continue connectin" {send -- "yes\r";}
      }
      stty echo
      sleep 1
      incr each
    }
    puts "MRVTS_SHOW_PORTS_END"
    return $output
  }
}

proc mrvTS {ts_ip ts_user ts_pass1 ts_pass2 ts_port {timeout 120}} {
  global spawn_id mrv0 mrv15 send_slow
  set mrv0 {([:]+[0-9\ ]+[>])}
  set mrv15 {>>}
  set output ""
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
          after 1000
          expect -re ".*" {send -s -- "\r\r\r";}
          after 1750
          break
        }
        -re $mrv0 {
          append output $expect_out(buffer)
          # logged-in
          # send -s -- "enable\r";
          append output $expect_out(buffer)
          after 500
          send -s -- "connect port async $ts_port \r";
          after 1000
          expect -re ".*" {send -s -- "\r \r \r \r \r"; append output $expect_out(buffer)}
          after 1750
          break
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
    while {$each <= 80} {
      expect {
         "nable to connect to port " {
          append output "\n\nBAREMETAL: MCC_LX_ERR    Unable to connect to port\n"
          append output $expect_out(buffer)
          return [mrvTS_Exit $output]
         }
         "Pulse Policy Secure" {
          append output "\n\nBAREMETAL: PULSE    ASCII_MENU\n"
          append output $expect_out(buffer)
          return [mrvTS_Exit $output]
         }
         "mcc" {
          # JUNIPER
          append output "\n\nBAREMETAL: MRV_MCC\n"
          append output $expect_out(buffer)
          return [mrvTS_Exit $output]
        }
        "{primary:node0}" {
          # JUNIPER
          append output "\n\nBAREMETAL: SRX    NOLOGIN\n"
          append output $expect_out(buffer)
          return [mrvTS_Exit $output]
        }
        -re "{\{master\}|-re0>|-re1>}" {
          # JUNIPER
          append output "\n\nBAREMETAL: MX    NOLOGIN\n"
          append output $expect_out(buffer)
          return [mrvTS_Exit $output]
        }
        "TH1040S" {
          append output "\n\nBAREMETAL: A10_THUNDER    LOGIN\n"
          append output $expect_out(buffer)
          return [mrvTS_Exit $output]
        }
        "root>" {
          # JUNIPER
          append output "\n\nBAREMETAL: JUNOS_CLI    NOLOGIN\n"
          append output $expect_out(buffer)
          return [mrvTS_Exit $output]
        }
        -re "{master:0}" {
          # JUNIPER
          append output "\n\nBAREMETAL: JUNIPER    CONFIG_MODE\n"
          append output $expect_out(buffer)
          return [mrvTS_Exit $output]
        }
        -re {root@:RE:0%|root@:RE:1%} {
          append output "\n\nBAREMETAL: PTX_MX    JUNOS_CLI\n"
          append output $expect_out(buffer)
          return [mrvTS_Exit $output]
        }
        "login: " {
          # JUNIPER
          append output "\n\nBAREMETAL: MX    LOGIN\n"
          append output $expect_out(buffer)
          return [mrvTS_Exit $output]
        }
        -re "{FreeBSD.*-re0|FreeBSD.*-re1}" {
          # JUNIPER
          append output "\n\nBAREMETAL: MX    LOGIN\n"
          append output $expect_out(buffer)
          return [mrvTS_Exit $output]
        }
        -re {([a-zA-Z0-9]+[@]+[a-zA-Z0-9\.\-\_]+[>#%])} {
          # JUNIPER
          append output "\n\nBAREMETAL: JUNIPER    NOLOGIN\n"
          append output $expect_out(buffer)
          return [mrvTS_Exit $output]
        }
        "POAP-2-POAP_INFO" {
          # NEXUS - ISSUES WITH POAP
          append output $expect_out(buffer)
          # return [mrvTS_Exit $output]
          send -s -- "\r \r \r \r";
        }
        -re {Power On Auto Provisioning] (yes/skip/no)|(yes/no)} {
          append output $expect_out(buffer)
          # return [mrvTS_Exit $output]
          send -s -- "yes\r  \r";
        }
        "Enter the password for" {
          append output "\n\nBAREMETAL: NEXUS    PASSWORD:\n"
          append output $expect_out(buffer)
          return [mrvTS_Exit $output]
        }
        "Nokia" {
          # accepts blank login == 7750
          append output "\n\nBAREMETAL: NOKIA    LOGIN\n"
          append output $expect_out(buffer)
          return [mrvTS_Exit $output]
        }
        "Login:" {
          append output "\n\nBAREMETAL: UNKNOWN    Login:\n"
          append output $expect_out(buffer)
          return [mrvTS_Exit $output]
        }
        -re  "OTHER" {
          append output "\n\nBAREMETAL: OTHER???\n"
          append output $expect_out(buffer)
          return [mrvTS_Exit $output]
         }
        "FreeBSD" {
          append output "\n\nBAREMETAL: BSD/Linux    UNKNOWN\n"
          append output $expect_out(buffer)
          return [mrvTS_Exit $output]
         }
        "SERVER" {
          append output "\n\nBAREMETAL: BSD/Linux    NOLOGIN\n"
          append output $expect_out(buffer)
          return [mrvTS_Exit $output]
         }
        -re ".*(\r|\n)" {
          after 2;
          append output $expect_out(buffer)
          exp_continue
        }
      }
      incr each
    }
    append output "\n\nBAREMETAL: TIMEOUT // EMPTY? \n"
    catch { append out $expect_out(bufer) }
    return [mrvTS_Exit $output]
  }
}

proc mrvTS_Exit {output} {
  catch { mrvTS_exit }
  append output "\n\n"
  return $output
}

proc is_pingable {router {options none}} {
     global ping_output
     set log_user [log_user -info]
     log_user 0
      if {[catch {set ping_output [exec ping -c 3 $router]} err]} {set ping_output $err}
     log_user $log_user
      switch -glob -- $ping_output {
        "* 0 received, *" -
        "* 0 packets received, *" -
        "* 1 packets received, *" -
        "* 1 received, *" {return 0}
        "* 5 packets received, *" -
        "* 4 packets received, *" -
        "* 3 packets received, *" -
        "* 2 packets received, *" -
        "* 5 received, *" -
        "* 4 received, *" -
        "* 3 received, *" -
        "* 2 received, *" {
          switch -- $options {
            "output" -
            "pingstats" {
              if {$log_user == 1} {
                send_user "\n\n[grep_until "ping statistics" "mdev" $ping_output]\n";
              }
            }
            "none" -
            default {}
          }
          return 1
        }
        default {
          switch -glob -- $err {
            "ping: unknown hos*" {return 0}
            default {
              if {$log_user == 1} {
                send_user "proc checkrouterup: '$err', re-code \n"
                send_user "\n\n '${ping_output}'\n";
              }
              return 0;
            }
          }
        }
      }
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

global argv_array
argv_array_run
