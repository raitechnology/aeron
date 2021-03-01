# defines a directory for build, for example, RH6_x86_64
lsb_dist     := $(shell if [ -x /usr/bin/lsb_release ] ; then lsb_release -is ; else uname -s ; fi)
lsb_dist_ver := $(shell if [ -x /usr/bin/lsb_release ] ; then lsb_release -rs | sed 's/[.].*//' ; else uname -r | sed 's/[-].*//' ; fi)
uname_m      := $(shell uname -m)

short_dist_lc := $(patsubst CentOS,rh,$(patsubst RedHatEnterprise,rh,\
                   $(patsubst RedHat,rh,\
                     $(patsubst Fedora,fc,$(patsubst Ubuntu,ub,\
                       $(patsubst Debian,deb,$(patsubst SUSE,ss,$(lsb_dist))))))))
short_dist    := $(shell echo $(short_dist_lc) | tr a-z A-Z)
pwd           := $(shell pwd)
rpm_os        := $(short_dist_lc)$(lsb_dist_ver).$(uname_m)

# this is where the targets are compiled
build_dir ?= $(short_dist)$(lsb_dist_ver)_$(uname_m)$(port_extra)
bind      := $(build_dir)/bin
libd      := $(build_dir)/lib64
objd      := $(build_dir)/obj
dependd   := $(build_dir)/dep

# use 'make port_extra=-g' for debug build
ifeq (-g,$(findstring -g,$(port_extra)))
  DEBUG = true
endif

CC          ?= gcc
CXX         ?= g++
cc          := $(CC) -std=c11
cpp         := $(CXX)
# if not linking libstdc++
ifdef NO_STL
cppflags    := -std=c++11 -fno-rtti -fno-exceptions
cpplink     := $(CC)
else
cppflags    := -std=c++11
cpplink     := $(CXX)
endif
clink       := $(CC)
arch_cflags := -fno-omit-frame-pointer
gcc_wflags  := -Wall -Wpedantic -Wextra -Wno-unused-parameter
fpicflags   := -fPIC -rdynamic
soflag      := -shared -rdynamic
rpath1      := -Wl,-rpath,$(pwd)/$(libd)

ifdef DEBUG
default_cflags := -ggdb
else
default_cflags := -O2 -Ofast -ggdb
endif
# rpmbuild uses RPM_OPT_FLAGS
#ifeq ($(RPM_OPT_FLAGS),)
#CFLAGS ?= $(default_cflags)
#else
#CFLAGS ?= $(RPM_OPT_FLAGS)
#endif
CFLAGS := $(default_cflags)
cflags := $(gcc_wflags) $(CFLAGS) $(arch_cflags)

# used in multiple places
aeron_defines := -D_DEFAULT_SOURCE -D_FILE_OFFSET_BITS=64
aeron_defines += -DDISABLE_BOUNDS_CHECKS -DHAVE_STRUCT_MMSGHDR -DHAVE_EPOLL
aeron_defines += -DHAVE_BSDSTDLIB_H -DHAVE_RECVMMSG -DHAVE_SENDMMSG

# uuid not really needed
# aeron_driver_context_defines = -DHAVE_UUID_H -DHAVE_UUID_GENERATE
aeron_driver_defines = -DHAVE_ARC4RANDOM

INCLUDES    ?= 
includes    := -Iaeron-client/src/main/c -Iaeron-driver/src/main/c $(INCLUDES)
DEFINES     ?= $(aeron_defines)
defines     := $(DEFINES)
cppdefines  := -DNDEBUG $(defines)
cpp_lnk     :=
sock_lib    :=
math_lib    := -lm
thread_lib  := -pthread -lrt

have_hdr_submodule  := $(shell if [ -d ./HdrHistogram_c ]; then echo yes; else echo no; fi )

lnk_lib     :=
dlnk_lib    :=

dlnk_lib    += -ldl -lbsd -lm
lnk_lib     += -ldl -lbsd -lm
malloc_lib  :=

# -luuid

ifeq (yes,$(have_hdr_submodule))
hdr_lib      := HdrHistogram_c/$(libd)/libhdrhist.a
hdr_dll      := HdrHistogram_c/$(libd)/libhdrhist.so
dlnk_hdr_lib += -LHdrHistogram_c/$(libd) -lhdrhist
dlnk_hdr_dep += $(hdr_dll)
rpath         = $(rpath1),-rpath,$(pwd)/HdrHistogram_c/$(libd)
includes     += -IHdrHistogram_c/src
else
dlnk_hdr_lib += -lhdrhist
dlnk_hdr_dep += -lhdrhist
rpath         = $(rpath1)
includes     += -I/usr/include/hdrhist
endif

cppincludes      := -Iaeron-client/src/main/cpp $(includes)
wrap_cppincludes := -Iaeron-client/src/main/cpp_wrapper $(includes)

# before include, that has srpm target
.PHONY: everything
everything: all

ifeq (yes,$(have_hdr_submodule))
$(hdr_lib) $(hdr_dll):
	$(MAKE) -C HdrHistogram_c
.PHONY: clean_hdr
clean_hdr:
	$(MAKE) -C HdrHistogram_c clean
endif

# copr/fedora build (with version env vars)
# copr uses this to generate a source rpm with the srpm target
-include .copr/Makefile

# debian build (debuild)
# target for building installable deb: dist_dpkg
-include deb/Makefile

# targets filled in below
all_exes    :=
cpp_exes    :=
all_libs    :=
cpp_libs    :=
all_depends :=
gen_files   :=
all_dirs    := $(bind) $(libd) $(objd) $(dependd)

client_collections_dir   := aeron-client/src/main/c/collections
client_collections_files := \
  aeron_array_to_ptr_hash_map aeron_bit_set aeron_int64_counter_map \
  aeron_int64_to_ptr_hash_map aeron_int64_to_tagged_ptr_hash_map aeron_map \
  aeron_str_to_ptr_hash_map

all_dirs += $(objd)/$(client_collections_dir) $(dependd)/$(client_collections_dir)

client_concurrent_dir   := aeron-client/src/main/c/concurrent
client_concurrent_files := \
  aeron_atomic aeron_broadcast_receiver aeron_broadcast_transmitter \
  aeron_counters_manager aeron_distinct_error_log \
  aeron_exclusive_term_appender aeron_logbuffer_descriptor \
  aeron_mpsc_concurrent_array_queue aeron_mpsc_rb \
  aeron_spsc_concurrent_array_queue aeron_spsc_rb aeron_term_appender \
  aeron_term_gap_filler aeron_term_gap_scanner aeron_term_rebuilder \
  aeron_term_scanner aeron_term_unblocker aeron_thread 

all_dirs += $(objd)/$(client_concurrent_dir) $(dependd)/$(client_concurrent_dir)

client_protocol_dir   := aeron-client/src/main/c/protocol
client_protocol_files := aeron_udp_protocol

all_dirs += $(objd)/$(client_protocol_dir) $(dependd)/$(client_protocol_dir)

client_reports_dir   := aeron-client/src/main/c/reports
client_reports_files := aeron_loss_reporter

all_dirs += $(objd)/$(client_reports_dir) $(dependd)/$(client_reports_dir)

client_status_dir   := aeron-client/src/main/c/status
client_status_files := aeron_local_sockaddr

all_dirs += $(objd)/$(client_status_dir) $(dependd)/$(client_status_dir)

client_util_dir   := aeron-client/src/main/c/util
client_util_files :=  \
  aeron_arrayutil aeron_bitutil aeron_clock aeron_dlopen aeron_env \
  aeron_error aeron_fileutil aeron_http_util aeron_math aeron_netutil \
  aeron_parse_util aeron_properties_util aeron_strutil

all_dirs += $(objd)/$(client_util_dir) $(dependd)/$(client_util_dir)

client_uri_dir   := aeron-client/src/main/c/uri
client_uri_files := aeron_uri

all_dirs += $(objd)/$(client_uri_dir) $(dependd)/$(client_uri_dir)

aeron_version_defines = -DAERON_VERSION_MAJOR=$(major_num) -DAERON_VERSION_MINOR=$(minor_num) -DAERON_VERSION_PATCH=$(patch_num) -DAERON_VERSION_TXT=\"$(ver_build)\"

client_dir   := aeron-client/src/main/c
client_files := \
  aeron_agent aeron_alloc aeron_client aeron_client_conductor \
  aeron_cnc aeron_cnc_file_descriptor aeron_context aeron_counter \
  aeron_exclusive_publication aeron_fragment_assembler aeron_image \
  aeron_log_buffer aeron_publication aeron_socket aeron_subscription \
  aeron_version aeron_windows aeronc

all_dirs += $(objd)/$(client_dir) $(dependd)/$(client_dir)

libaeron_static_objs = \
  $(addprefix $(objd)/$(client_collections_dir)/, $(addsuffix .o, $(notdir $(client_collections_files)))) \
  $(addprefix $(objd)/$(client_concurrent_dir)/, $(addsuffix .o, $(notdir $(client_concurrent_files)))) \
  $(addprefix $(objd)/$(client_protocol_dir)/, $(addsuffix .o, $(notdir $(client_protocol_files)))) \
  $(addprefix $(objd)/$(client_reports_dir)/, $(addsuffix .o, $(notdir $(client_reports_files)))) \
  $(addprefix $(objd)/$(client_status_dir)/, $(addsuffix .o, $(notdir $(client_status_files)))) \
  $(addprefix $(objd)/$(client_util_dir)/, $(addsuffix .o, $(notdir $(client_util_files)))) \
  $(addprefix $(objd)/$(client_uri_dir)/, $(addsuffix .o, $(notdir $(client_uri_files)))) \
  $(addprefix $(objd)/$(client_dir)/, $(addsuffix .o, $(notdir $(client_files))))
libaeron_static_deps = \
  $(addprefix $(dependd)/$(client_collections_dir)/, $(addsuffix .d, $(notdir $(client_collections_files)))) \
  $(addprefix $(dependd)/$(client_concurrent_dir)/, $(addsuffix .d, $(notdir $(client_concurrent_files)))) \
  $(addprefix $(dependd)/$(client_protocol_dir)/, $(addsuffix .d, $(notdir $(client_protocol_files)))) \
  $(addprefix $(dependd)/$(client_reports_dir)/, $(addsuffix .d, $(notdir $(client_reports_files)))) \
  $(addprefix $(dependd)/$(client_status_dir)/, $(addsuffix .d, $(notdir $(client_status_files)))) \
  $(addprefix $(dependd)/$(client_util_dir)/, $(addsuffix .d, $(notdir $(client_util_files)))) \
  $(addprefix $(dependd)/$(client_uri_dir)/, $(addsuffix .d, $(notdir $(client_uri_files)))) \
  $(addprefix $(dependd)/$(client_dir)/, $(addsuffix .d, $(notdir $(client_files))))

$(libd)/libaeron_static.a: $(libaeron_static_objs)

all_libs    += $(libd)/libaeron_static.a
all_depends += $(libaeron_static_deps)

libaeron_dbjs = \
  $(addprefix $(objd)/$(client_collections_dir)/, $(addsuffix .fpic.o, $(notdir $(client_collections_files)))) \
  $(addprefix $(objd)/$(client_concurrent_dir)/, $(addsuffix .fpic.o, $(notdir $(client_concurrent_files)))) \
  $(addprefix $(objd)/$(client_protocol_dir)/, $(addsuffix .fpic.o, $(notdir $(client_protocol_files)))) \
  $(addprefix $(objd)/$(client_reports_dir)/, $(addsuffix .fpic.o, $(notdir $(client_reports_files)))) \
  $(addprefix $(objd)/$(client_status_dir)/, $(addsuffix .fpic.o, $(notdir $(client_status_files)))) \
  $(addprefix $(objd)/$(client_util_dir)/, $(addsuffix .fpic.o, $(notdir $(client_util_files)))) \
  $(addprefix $(objd)/$(client_uri_dir)/, $(addsuffix .fpic.o, $(notdir $(client_uri_files)))) \
  $(addprefix $(objd)/$(client_dir)/, $(addsuffix .fpic.o, $(notdir $(client_files))))
libaeron_deps = \
  $(addprefix $(dependd)/$(client_collections_dir)/, $(addsuffix .fpic.d, $(notdir $(client_collections_files)))) \
  $(addprefix $(dependd)/$(client_concurrent_dir)/, $(addsuffix .fpic.d, $(notdir $(client_concurrent_files)))) \
  $(addprefix $(dependd)/$(client_protocol_dir)/, $(addsuffix .fpic.d, $(notdir $(client_protocol_files)))) \
  $(addprefix $(dependd)/$(client_reports_dir)/, $(addsuffix .fpic.d, $(notdir $(client_reports_files)))) \
  $(addprefix $(dependd)/$(client_status_dir)/, $(addsuffix .fpic.d, $(notdir $(client_status_files)))) \
  $(addprefix $(dependd)/$(client_util_dir)/, $(addsuffix .fpic.d, $(notdir $(client_util_files)))) \
  $(addprefix $(dependd)/$(client_uri_dir)/, $(addsuffix .fpic.d, $(notdir $(client_uri_files)))) \
  $(addprefix $(dependd)/$(client_dir)/, $(addsuffix .fpic.d, $(notdir $(client_files))))
libaeron_dlnk  := $(dlnk_lib)
libaeron_spec  := $(version)-$(build_num)
libaeron_ver   := $(major_num).$(minor_num)

$(libd)/libaeron.so: $(libaeron_dbjs)

all_libs    += $(libd)/libaeron.so
all_depends += $(libaeron_deps)

driver_agent_dir   := aeron-driver/src/main/c/agent
driver_agent_files := aeron_driver_agent

all_dirs += $(objd)/$(driver_agent_dir) $(dependd)/$(driver_agent_dir)

driver_concurrent_dir   := aeron-driver/src/main/c/concurrent
driver_concurrent_files := aeron_logbuffer_unblocker

all_dirs += $(objd)/$(driver_concurrent_dir) $(dependd)/$(driver_concurrent_dir)

driver_media_dir   := aeron-driver/src/main/c/media
driver_media_files := \
  aeron_receive_channel_endpoint aeron_receive_destination \
  aeron_send_channel_endpoint aeron_udp_channel \
  aeron_udp_channel_transport aeron_udp_channel_transport_bindings \
  aeron_udp_channel_transport_loss aeron_udp_destination_tracker \
  aeron_udp_transport_poller

all_dirs += $(objd)/$(driver_media_dir) $(dependd)/$(driver_media_dir)

driver_uri_dir   := aeron-driver/src/main/c/uri
driver_uri_files := aeron_driver_uri

all_dirs += $(objd)/$(driver_uri_dir) $(dependd)/$(driver_uri_dir)

driver_dir   := aeron-driver/src/main/c
driver_files := \
  aeron_congestion_control aeron_csv_table_name_resolver \
  aeron_data_packet_dispatcher aeron_driver aeron_driver_conductor \
  aeron_driver_conductor_proxy aeron_driver_context \
  aeron_driver_name_resolver aeron_driver_receiver \
  aeron_driver_receiver_proxy aeron_driver_sender \
  aeron_driver_sender_proxy aeron_flow_control aeron_ipc_publication \
  aeron_loss_detector aeron_min_flow_control aeron_name_resolver \
  aeron_name_resolver_cache aeron_network_publication aeron_position \
  aeron_publication_image aeron_retransmit_handler \
  aeron_system_counters aeron_termination_validator

all_dirs += $(objd)/$(driver_dir) $(dependd)/$(driver_dir)

libaeron_driver_static_objs = \
  $(libaeron_static_objs) \
  $(addprefix $(objd)/$(driver_agent_dir)/, $(addsuffix .o, $(notdir $(driver_agent_files)))) \
  $(addprefix $(objd)/$(driver_concurrent_dir)/, $(addsuffix .o, $(notdir $(driver_concurrent_files)))) \
  $(addprefix $(objd)/$(driver_media_dir)/, $(addsuffix .o, $(notdir $(driver_media_files)))) \
  $(addprefix $(objd)/$(driver_uri_dir)/, $(addsuffix .o, $(notdir $(driver_uri_files)))) \
  $(addprefix $(objd)/$(driver_dir)/, $(addsuffix .o, $(notdir $(driver_files))))
libaeron_driver_static_deps = \
  $(addprefix $(dependd)/$(driver_agent_dir)/, $(addsuffix .d, $(notdir $(driver_agent_files)))) \
  $(addprefix $(dependd)/$(driver_concurrent_dir)/, $(addsuffix .d, $(notdir $(driver_concurrent_files)))) \
  $(addprefix $(dependd)/$(driver_media_dir)/, $(addsuffix .d, $(notdir $(driver_media_files)))) \
  $(addprefix $(dependd)/$(driver_uri_dir)/, $(addsuffix .d, $(notdir $(driver_uri_files)))) \
  $(addprefix $(dependd)/$(driver_dir)/, $(addsuffix .d, $(notdir $(driver_files))))

$(libd)/libaeron_driver_static.a: $(libaeron_driver_static_objs)

all_libs    += $(libd)/libaeron_driver_static.a
all_depends += $(libaeron_driver_static_deps)

libaeron_driver_dbjs = \
  $(libaeron_dbjs) \
  $(addprefix $(objd)/$(driver_agent_dir)/, $(addsuffix .fpic.o, $(notdir $(driver_agent_files)))) \
  $(addprefix $(objd)/$(driver_concurrent_dir)/, $(addsuffix .fpic.o, $(notdir $(driver_concurrent_files)))) \
  $(addprefix $(objd)/$(driver_media_dir)/, $(addsuffix .fpic.o, $(notdir $(driver_media_files)))) \
  $(addprefix $(objd)/$(driver_uri_dir)/, $(addsuffix .fpic.o, $(notdir $(driver_uri_files)))) \
  $(addprefix $(objd)/$(driver_dir)/, $(addsuffix .fpic.o, $(notdir $(driver_files))))
libaeron_driver_deps = \
  $(addprefix $(dependd)/$(driver_agent_dir)/, $(addsuffix .fpic.d, $(notdir $(driver_agent_files)))) \
  $(addprefix $(dependd)/$(driver_concurrent_dir)/, $(addsuffix .fpic.d, $(notdir $(driver_concurrent_files)))) \
  $(addprefix $(dependd)/$(driver_media_dir)/, $(addsuffix .fpic.d, $(notdir $(driver_media_files)))) \
  $(addprefix $(dependd)/$(driver_uri_dir)/, $(addsuffix .fpic.d, $(notdir $(driver_uri_files)))) \
  $(addprefix $(dependd)/$(driver_dir)/, $(addsuffix .fpic.d, $(notdir $(driver_files))))
libaeron_driver_dlnk = $(dlnk_lib)
libaeron_driver_spec = $(version)-$(build_num)
libaeron_driver_ver  = $(major_num).$(minor_num)

$(libd)/libaeron_driver.so: $(libaeron_driver_dbjs)

all_libs    += $(libd)/libaeron_driver.so
all_depends += $(libaeron_driver_deps)

Aeron_defines := -DAERON_VERSION_MAJOR=$(major_num) -DAERON_VERSION_MINOR=$(minor_num) -DAERON_VERSION_PATCH=$(patch_num) -DAERON_VERSION_TXT=\"$(version)\"

clientcpp_dir   := aeron-client/src/main/cpp
clientcpp_files := \
  Publication ExclusivePublication Subscription ClientConductor Aeron \
  LogBuffers Counter Context

all_dirs += $(objd)/$(clientcpp_dir) $(dependd)/$(clientcpp_dir)

utilcpp_dir   := aeron-client/src/main/cpp/util
utilcpp_files := MemoryMappedFile CommandOption CommandOptionParser

all_dirs += $(objd)/$(utilcpp_dir) $(dependd)/$(utilcpp_dir)

libaeron_client_objs = \
  $(addprefix $(objd)/$(clientcpp_dir)/, $(addsuffix .o, $(notdir $(clientcpp_files)))) \
  $(addprefix $(objd)/$(utilcpp_dir)/, $(addsuffix .o, $(notdir $(utilcpp_files))))
libaeron_client_deps = \
  $(addprefix $(dependd)/$(clientcpp_dir)/, $(addsuffix .d, $(notdir $(clientcpp_files)))) \
  $(addprefix $(dependd)/$(utilcpp_dir)/, $(addsuffix .d, $(notdir $(utilcpp_files))))

$(libd)/libaeron_client.a: $(libaeron_client_objs)

all_libs    += $(libd)/libaeron_client.a
all_depends += $(libaeron_client_deps)

libaeron_client_shared_dbjs = \
  $(addprefix $(objd)/$(clientcpp_dir)/, $(addsuffix .fpic.o, $(notdir $(clientcpp_files)))) \
  $(addprefix $(objd)/$(utilcpp_dir)/, $(addsuffix .fpic.o, $(notdir $(utilcpp_files))))
libaeron_client_shared_deps = \
  $(addprefix $(dependd)/$(clientcpp_dir)/, $(addsuffix .fpic.d, $(notdir $(clientcpp_files)))) \
  $(addprefix $(dependd)/$(utilcpp_dir)/, $(addsuffix .fpic.d, $(notdir $(utilcpp_files))))
libaeron_client_shared_dlnk = $(dlnk_lib)
libaeron_client_shared_spec = $(version)-$(build_num)
libaeron_client_shared_ver  = $(major_num).$(minor_num)

$(libd)/libaeron_client_shared.so: $(libaeron_client_shared_dbjs)

cpp_libs    += $(libd)/libaeron_client_shared.so
all_libs    += $(libd)/libaeron_client_shared.so
all_depends += $(libaeron_client_shared_deps)

aeronmd_files = aeronmd
aeronmd_objs  = $(addprefix $(objd)/$(driver_dir)/, $(addsuffix .o, $(notdir $(aeronmd_files))))
aeronmd_deps  = $(addprefix $(dependd)/$(driver_dir)/, $(addsuffix .d, $(notdir $(aeronmd_files))))
aeronmd_libs  = $(libd)/libaeron_driver.so
aeronmd_lnk   = -laeron_driver

$(bind)/aeronmd: $(aeronmd_objs) $(aeronmd_libs)

all_exes    += $(bind)/aeronmd
all_depends += $(aeronmd_deps)

samples_dir   := aeron-samples/src/main/c
samples_files := \
  basic_publisher basic_subscriber cping cpong rate_subscriber \
  sample_util streaming_exclusive_publisher streaming_publisher \
  aeron_stat

all_dirs += $(objd)/$(samples_dir) $(dependd)/$(samples_dir)

basic_publisher_lnk  = -laeron
basic_publisher_objs = $(objd)/$(samples_dir)/basic_publisher.o
$(bind)/basic_publisher: $(basic_publisher_objs) $(libd)/libaeron.so

basic_subscriber_lnk  = -laeron
basic_subscriber_objs = $(objd)/$(samples_dir)/basic_subscriber.o \
                        $(objd)/$(samples_dir)/sample_util.o
$(bind)/basic_subscriber: $(basic_subscriber_objs) $(libd)/libaeron.so

cping_lnk  = -laeron $(dlnk_hdr_lib)
cping_objs = $(objd)/$(samples_dir)/cping.o \
             $(objd)/$(samples_dir)/sample_util.o
$(bind)/cping: $(cping_objs) $(libd)/libaeron.so $(dlnk_hdr_dep)

cpong_lnk  = -laeron
cpong_objs = $(objd)/$(samples_dir)/cpong.o \
             $(objd)/$(samples_dir)/sample_util.o
$(bind)/cpong: $(cpong_objs) $(libd)/libaeron.so

rate_subscriber_lnk  = -laeron
rate_subscriber_objs = $(objd)/$(samples_dir)/rate_subscriber.o \
                       $(objd)/$(samples_dir)/sample_util.o
$(bind)/rate_subscriber: $(rate_subscriber_objs) $(libd)/libaeron.so

streaming_exclusive_publisher_lnk  = -laeron
streaming_exclusive_publisher_objs = $(objd)/$(samples_dir)/streaming_exclusive_publisher.o \
                                     $(objd)/$(samples_dir)/sample_util.o
$(bind)/streaming_exclusive_publisher: $(streaming_exclusive_publisher_objs) $(libd)/libaeron.so

streaming_publisher_lnk  = -laeron
streaming_publisher_objs = $(objd)/$(samples_dir)/streaming_publisher.o \
                           $(objd)/$(samples_dir)/sample_util.o
$(bind)/streaming_publisher: $(streaming_publisher_objs) $(libd)/libaeron.so

aeron_stat_lnk  = -laeron
aeron_stat_objs = $(objd)/$(samples_dir)/aeron_stat.o
$(bind)/aeron_stat: $(aeron_stat_objs) $(libd)/libaeron.so

loss_stat_lnk  = -laeron
loss_stat_objs = $(objd)/$(samples_dir)/loss_stat.o
$(bind)/loss_stat: $(loss_stat_objs) $(libd)/libaeron.so

all_exes    += $(bind)/basic_publisher $(bind)/basic_subscriber $(bind)/cping
all_exes    += $(bind)/cpong $(bind)/rate_subscriber
all_exes    += $(bind)/streaming_exclusive_publisher $(bind)/streaming_publisher
all_exes    += $(bind)/aeron_stat $(bind)/loss_stat
all_depends += $(addprefix $(dependd)/$(samples_dir)/, $(addsuffix .d, $(notdir $(samples_files))))

samplescpp_dir = aeron-samples/src/main/cpp
samplescpp_files = \
  BasicPublisher BasicSubscriber StreamingPublisher RateSubscriber \
  Pong Ping Throughput ExclusiveThroughput PingPong

all_dirs += $(objd)/$(samplescpp_dir) $(dependd)/$(samplescpp_dir)
all_depends += $(addprefix $(dependd)/$(samplescpp_dir)/, $(addsuffix .d, $(notdir $(samplescpp_files))))

BasicPublisher_lnk  = -laeron_client_shared
BasicPublisher_objs = $(objd)/$(samplescpp_dir)/BasicPublisher.o
$(bind)/BasicPublisher: $(BasicPublisher_objs) $(libd)/libaeron_client_shared.so

BasicPublisherW_lnk  = -laeron
BasicPublisherW_objs = $(objd)/$(samplescpp_dir)/BasicPublisher.owrap
$(bind)/BasicPublisherW: $(BasicPublisherW_objs) $(libd)/libaeron.so

BasicSubscriber_lnk  = -laeron_client_shared
BasicSubscriber_objs = $(objd)/$(samplescpp_dir)/BasicSubscriber.o
$(bind)/BasicSubscriber: $(BasicSubscriber_objs) $(libd)/libaeron_client_shared.so

BasicSubscriberW_lnk  = -laeron
BasicSubscriberW_objs = $(objd)/$(samplescpp_dir)/BasicSubscriber.owrap
$(bind)/BasicSubscriberW: $(BasicSubscriberW_objs) $(libd)/libaeron.so

StreamingPublisher_lnk = -laeron_client_shared
StreamingPublisher_objs = $(objd)/$(samplescpp_dir)/StreamingPublisher.o
$(bind)/StreamingPublisher: $(StreamingPublisher_objs) $(libd)/libaeron_client_shared.so

StreamingPublisherW_lnk = -laeron
StreamingPublisherW_objs = $(objd)/$(samplescpp_dir)/StreamingPublisher.owrap
$(bind)/StreamingPublisherW: $(StreamingPublisherW_objs) $(libd)/libaeron.so

RateSubscriber_lnk = -laeron_client_shared
RateSubscriber_objs = $(objd)/$(samplescpp_dir)/RateSubscriber.o
$(bind)/RateSubscriber: $(RateSubscriber_objs) $(libd)/libaeron_client_shared.so

RateSubscriberW_lnk = -laeron
RateSubscriberW_objs = $(objd)/$(samplescpp_dir)/RateSubscriber.owrap
$(bind)/RateSubscriberW: $(RateSubscriberW_objs) $(libd)/libaeron.so

Ping_lnk = -laeron_client_shared $(dlnk_hdr_lib)
Ping_objs = $(objd)/$(samplescpp_dir)/Ping.o
$(bind)/Ping: $(Ping_objs) $(libd)/libaeron_client_shared.so $(dlnk_hdr_dep)

PingW_lnk = -laeron $(dlnk_hdr_lib)
PingW_objs = $(objd)/$(samplescpp_dir)/Ping.owrap
$(bind)/PingW: $(PingW_objs) $(libd)/libaeron.so $(dlnk_hdr_dep)

Pong_lnk = -laeron_client_shared
Pong_objs = $(objd)/$(samplescpp_dir)/Pong.o
$(bind)/Pong: $(Pong_objs) $(libd)/libaeron_client_shared.so

PongW_lnk = -laeron
PongW_objs = $(objd)/$(samplescpp_dir)/Pong.owrap
$(bind)/PongW: $(PongW_objs) $(libd)/libaeron.so

Throughput_lnk  = -laeron_client_shared
Throughput_objs = $(objd)/$(samplescpp_dir)/Throughput.o
$(bind)/Throughput: $(Throughput_objs) $(libd)/libaeron_client_shared.so

ExclusiveThroughput_lnk  = -laeron_client_shared
ExclusiveThroughput_objs = $(objd)/$(samplescpp_dir)/ExclusiveThroughput.o
$(bind)/ExclusiveThroughput: $(ExclusiveThroughput_objs) $(libd)/libaeron_client_shared.so

PingPong_lnk  = -laeron_client_shared $(dlnk_hdr_lib)
PingPong_objs = $(objd)/$(samplescpp_dir)/PingPong.o
$(bind)/PingPong: $(PingPong_objs) $(libd)/libaeron_client_shared.so $(dlnk_hdr_dep)

samplesrawcpp_dir   := aeron-samples/src/main/cpp/raw
samplesrawcpp_files := TimeTests

all_dirs += $(objd)/$(samplesrawcpp_dir) $(dependd)/$(samplesrawcpp_dir)
all_depends += $(addprefix $(dependd)/$(samplesrawcpp_dir)/, $(addsuffix .d, $(notdir $(samplesrawcpp_files))))

TimeTests_objs = $(objd)/$(samplesrawcpp_dir)/TimeTests.o
$(bind)/TimeTests: $(TimeTests_objs)

cpp_exes += $(bind)/BasicPublisher $(bind)/BasicSubscriber
cpp_exes += $(bind)/BasicPublisherW $(bind)/BasicSubscriberW
cpp_exes += $(bind)/StreamingPublisher $(bind)/RateSubscriber
cpp_exes += $(bind)/StreamingPublisherW $(bind)/RateSubscriberW
cpp_exes += $(bind)/Pong $(bind)/Ping $(bind)/Throughput
cpp_exes += $(bind)/PongW $(bind)/PingW
cpp_exes += $(bind)/ExclusiveThroughput $(bind)/PingPong
cpp_exes += $(bind)/TimeTests
all_exes += $(cpp_exes)

# the default targets
.PHONY: all
all: $(all_libs) $(all_exes)

# create directories
$(dependd):
	@mkdir -p $(all_dirs)

# remove target bins, objs, depends
.PHONY: clean
clean:
	rm -rf $(bind) $(libd) $(objd) $(dependd)
	if [ "$(build_dir)" != "." ] ; then rmdir $(build_dir) ; fi

.PHONY: clean_dist
clean_dist:
	rm -rf dpkgbuild rpmbuild

.PHONY: clean_all
clean_all: clean clean_dist

# force a remake of depend using 'make -B depend'
.PHONY: depend
depend: $(dependd)/depend.make

$(dependd)/depend.make: $(dependd) $(all_depends)
	@echo "# depend file" > $(dependd)/depend.make
	@cat $(all_depends) >> $(dependd)/depend.make

ifeq (SunOS,$(lsb_dist))
remove_rpath = rpath -r
else
remove_rpath = chrpath -d
endif

# build all, then remove run paths embedded (use /etc/ld.conf.d instead)
.PHONY: dist_bins
dist_bins: all
	$(remove_rpath) $(bind)/*
	$(remove_rpath) $(libd)/*.so

.PHONY: dist_rpm
dist_rpm: srpm
	( cd rpmbuild && rpmbuild --define "-topdir `pwd`" -ba SPECS/aeron.spec )

# dependencies made by 'make depend'
-include $(dependd)/depend.make

ifeq ($(DESTDIR),)
# 'sudo make install' puts things in /usr/local/lib, /usr/local/include
install_prefix ?= /usr/local
else
# debuild uses DESTDIR to put things into debian/libdecnumber/usr
install_prefix = $(DESTDIR)/usr
endif
# this should be 64 for rpm based, /64 for SunOS
install_lib_suffix ?=

# create directory structure and copy for lib bin include
install: all
	# install all binaries
	install -d $(install_prefix)/bin
	install $(bind)/* $(install_prefix)/bin
	$(remove_rpath) $(install_prefix)/bin/*
	# install lib, keep symlinks intact
	install -d $(install_prefix)/lib$(install_lib_suffix)
	for f in $(libd)/* ; do \
	if [ -h $$f ] ; then \
	cp -a $$f $(install_prefix)/lib$(install_lib_suffix) ; \
	else \
	install $$f $(install_prefix)/lib$(install_lib_suffix) ; \
	fi ; \
	done
	$(remove_rpath) $(install_prefix)/lib$(install_lib_suffix)/*.so
	# install include files: cpp client, c client, media driver
	install -d $(install_prefix)/include
	for i in $$(find aeron-client/src/main/cpp/ -type d -print) ; do \
	install -d $$i $(install_prefix)/include/$${i#aeron-client/src/main/cpp/} ; \
	done
	for i in $$(find aeron-client/src/main/cpp/ -name '*.h' -print) ; do \
	install -m 644 $$i $(install_prefix)/include/$${i#aeron-client/src/main/cpp/} ; \
	done
	install -d $(install_prefix)/include/aeron
	for i in $$(find aeron-client/src/main/c/ -type d -print) ; do \
	install -d $$i $(install_prefix)/include/aeron/$${i#aeron-client/src/main/c/} ; \
	done
	for i in $$(find aeron-client/src/main/c/ -name '*.h' -print) ; do \
	install -m 644 $$i $(install_prefix)/include/aeron/$${i#aeron-client/src/main/c/} ; \
	done
	install -d $(install_prefix)/include/aeronmd
	for i in $$(find aeron-driver/src/main/c/ -type d -print) ; do \
	install -d $$i $(install_prefix)/include/aeronmd/$${i#aeron-driver/src/main/c/} ; \
	done
	for i in $$(find aeron-driver/src/main/c/ -name '*.h' -print) ; do \
	install -m 644 $$i $(install_prefix)/include/aeronmd/$${i#aeron-driver/src/main/c/} ; \
	done

$(objd)/%.o: %.cpp
	$(cpp) $(cflags) $(cppflags) $(cppincludes) $(cppdefines) $($(notdir $*)_includes) $($(notdir $*)_defines) -c $< -o $@

$(objd)/%.owrap: %.cpp
	$(cpp) $(cflags) $(cppflags) $(wrap_cppincludes) $(cppdefines) $($(notdir $*)_includes) $($(notdir $*)_defines) -c $< -o $@

$(objd)/%.o: %.c
	$(cc) $(cflags) $(includes) $(defines) $($(notdir $*)_includes) $($(notdir $*)_defines) -c $< -o $@

$(objd)/%.fpic.o: %.cpp
	$(cpp) $(cflags) $(fpicflags) $(cppflags) $(cppincludes) $(cppdefines) $($(notdir $*)_includes) $($(notdir $*)_defines) -c $< -o $@

$(objd)/%.fpic.o: %.c
	$(cc) $(cflags) $(fpicflags) $(includes) $(defines) $($(notdir $*)_includes) $($(notdir $*)_defines) -c $< -o $@

$(libd)/%.a:
	ar rc $@ $($(*)_objs)

$(libd)/%.so:
	$(if $(findstring $@, $(cpp_libs)),$(cpplink),$(clink)) $(soflag) $(rpath) $(cflags) -o $@.$($(*)_spec) -Wl,-soname=$(@F).$($(*)_ver) $($(*)_dbjs) $($(*)_dlnk) $(cpp_dll_lnk) $(sock_lib) $(math_lib) $(thread_lib) $(malloc_lib) $(dynlink_lib) && \
	cd $(libd) && ln -f -s $(@F).$($(*)_spec) $(@F).$($(*)_ver) && ln -f -s $(@F).$($(*)_ver) $(@F)

$(bind)/%:
	$(if $(findstring $@, $(cpp_exes)),$(cpplink),$(clink)) $(cflags) $(rpath) -o $@ $($(*)_objs) -L$(libd) $($(*)_lnk) $(cpp_lnk) $(sock_lib) $(math_lib) $(thread_lib) $(malloc_lib) $(dynlink_lib)

$(dependd)/%.d: %.cpp
	$(cpp) $(arch_cflags) $(cppflags) $(cppdefines) $(cppincludes) $($(notdir $*)_includes) $($(notdir $*)_defines) -MM $< -MT $(objd)/$(*).o -MF $@

$(dependd)/%.d: %.c
	$(cc) $(arch_cflags) $(defines) $(includes) $($(notdir $*)_includes) $($(notdir $*)_defines) -MM $< -MT $(objd)/$(*).o -MF $@

$(dependd)/%.fpic.d: %.cpp
	$(cpp) $(arch_cflags) $(cppflags) $(cppdefines) $(cppincludes) $($(notdir $*)_includes) $($(notdir $*)_defines) -MM $< -MT $(objd)/$(*).fpic.o -MF $@

$(dependd)/%.fpic.d: %.c
	$(cc) $(arch_cflags) $(defines) $(includes) $($(notdir $*)_includes) $($(notdir $*)_defines) -MM $< -MT $(objd)/$(*).fpic.o -MF $@
