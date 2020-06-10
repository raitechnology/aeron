outdir ?= rpmbuild/SRPMS
name   := aeron
spec   := rpm/$(name).spec
date   := $(shell date +"%a %b %d %Y")
rpmdir := $(shell pwd)

testfile = $(shell if [ -f $(1) ]; then echo true; fi)

ifeq ($(call testfile,version.txt),true)
version_txt := $(shell cat version.txt | sed 's/[.-]/ /g')
major_num   := $(word 1, $(version_txt))
minor_num   := $(word 2, $(version_txt))
patch_num   := $(word 3, $(version_txt))
build_num   := $(word 4, $(version_txt))
endif
ifeq (,$(major_num))
major_num   := 99
endif
ifeq (,$(minor_num))
minor_num   := 99
endif
ifeq (,$(patch_num))
patch_num   := 99
endif
ifeq (,$(build_num))
build_num   := 0
endif

version     := $(major_num).$(minor_num).$(patch_num)
ver_build   := $(version)-$(build_num)
name_ver    := $(name)-$(ver_build)
rpm_src_dir := rpmbuild/SOURCES/$(name)-$(version)
srctree     := aeron-agent aeron-archive aeron-client aeron-cluster \
	       aeron-driver aeron-samples aeron-system-tests \
	       aeron-test-support build.gradle buildSrc CMakeLists.txt config \
	       CONTRIBUTING.md gradle gradle.properties gradlew \
	       gradlew.bat LICENSE README.md run-ci-tests.sh settings.gradle \
	       version.txt GNUmakefile .copr deb rpm

.PHONY: srpm
srpm: $(outdir)/$(name)-$(version)-$(release).src.rpm

$(outdir)/$(name)-$(version)-$(release).src.rpm: rpmbuild/SOURCES/$(name_ver).tar.gz
	mkdir -p $(outdir)
	rpmbuild --root $(rpmdir) -D'_topdir rpmbuild' -D'_srcrpmdir $(outdir)' -D'_sourcedir rpmbuild/SOURCES' -bs rpmbuild/SPECS/$(name).spec

rpmbuild/SOURCES/$(name_ver).tar.gz:
	mkdir -p rpmbuild/RPMS rpmbuild/SRPMS rpmbuild/BUILD rpmbuild/SOURCES rpmbuild/SPECS
	sed -e "s/99999/${build_num}/" \
	    -e "s/999.999/${version}/" \
	    -e "s/__DATE__/${date}/" < rpm/$(name).spec > rpmbuild/SPECS/$(name).spec
	mkdir -p $(rpm_src_dir)
	for i in $(srctree) ; do ln -sf ../../../$$i $(rpm_src_dir) ; done
	( cd rpmbuild/SOURCES ; tar chzf $(name_ver).tar.gz --exclude=".*.sw*" $(name)-$(version) && rm -rf $(name)-$(version) )

