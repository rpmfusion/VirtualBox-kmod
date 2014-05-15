# buildforkernels macro hint: when you build a new version or a new release
# that contains bugfixes or other improvements then you must disable the
# "buildforkernels newest" macro for just that build; immediately after
# queuing that build enable the macro again for subsequent builds; that way
# a new akmod package will only get build when a new one is actually needed
%global buildforkernels newest

# In prerelease builds (such as betas), this package has the same
# major version number, while the kernel module abi is not guarranteed
# to be stable. This is so that we force the module update in sync with
# userspace.
#global prerel RC4
%global prereltag %{?prerel:_%(awk 'BEGIN {print toupper("%{prerel}")}')}

%global vboxrel 1
%global vboxreltag %{?vboxrel:-%{vboxrel}}
# Allow only root to access vboxdrv regardless of the file mode
# use only for debugging!
%bcond_with hardening

Name:           VirtualBox-kmod
Version:        4.3.10
Release:        1%{?prerel:.%{prerel}}%{?dist}.7

Summary:        Kernel module for VirtualBox
Group:          System Environment/Kernel
License:        GPLv2 or CDDL
URL:            http://www.virtualbox.org/wiki/VirtualBox
# This filters out the XEN kernel, since we don't run on XEN
Source1:        VirtualBox-OSE-kmod-1.6.4-kernel-variants.txt

%global AkmodsBuildRequires %{_bindir}/kmodtool, VirtualBox-kmodsrc >= %{version}%{vboxreltag}, xz, time
BuildRequires:  %{AkmodsBuildRequires}

# needed for plague to make sure it builds for i586 and i686
ExclusiveArch:  i686 x86_64

# get the proper build-sysbuild package from the repo, which
# tracks in all the kernel-devel packages
%{!?kernels:BuildRequires: buildsys-build-rpmfusion-kerneldevpkgs-%{?buildforkernels:%{buildforkernels}}%{!?buildforkernels:current}-%{_target_cpu} }

# kmodtool does its magic here
%{expand:%(kmodtool --target %{_target_cpu} --repo rpmfusion --kmodname %{name} %{?buildforkernels:--%{buildforkernels}} %{?kernels:--for-kernels "%{?kernels}"} --filterfile %{SOURCE1} --obsolete-name VirtualBox-OSE --obsolete-version %{version}-%{release} 2>/dev/null) }


%description
Kernel module for VirtualBox


%prep
%setup -T -c
tar --use-compress-program xz -xf %{_datadir}/%{name}-%{version}/%{name}-%{version}.tar.xz

# error out if there was something wrong with kmodtool
%{?kmodtool_check}

# print kmodtool output for debugging purposes:
kmodtool --target %{_target_cpu}  --repo rpmfusion --kmodname %{name} %{?buildforkernels:--%{buildforkernels}} %{?kernels:--for-kernels "%{?kernels}"} --filterfile %{SOURCE1} --obsolete-name VirtualBox-OSE --obsolete-version %{version}-%{release} 2>/dev/null

# This is hardcoded in Makefiles
# Kto zisti, preco tu nefunguje %%without hardening ma u mna nanuk
%{?with_hardening:find %{name}-%{version} -name Makefile |xargs sed 's/-DVBOX_WITH_HARDENING//' -i}

for kernel_version in %{?kernel_versions} ; do
    cp -al %{name}-%{version} _kmod_build_${kernel_version%%___*}
done


%build
for kernel_version in %{?kernel_versions}; do
    for module in vbox{drv,guest}; do
        make VBOX_USE_INSERT_PAGE=1 %{?_smp_mflags} -C "${kernel_version##*___}" SUBDIRS="${PWD}/_kmod_build_${kernel_version%%___*}/${module}"  modules
    done
    cp _kmod_build_${kernel_version%%___*}/{vboxdrv/Module.symvers,vboxnetadp}
    cp _kmod_build_${kernel_version%%___*}/{vboxdrv/Module.symvers,vboxnetflt}
    cp _kmod_build_${kernel_version%%___*}/{vboxguest/Module.symvers,vboxsf}
    cp _kmod_build_${kernel_version%%___*}/{vboxguest/Module.symvers,vboxvideo}
    for module in vbox{netadp,netflt,sf,video,pci}; do
        make VBOX_USE_INSERT_PAGE=1 %{?_smp_mflags} -C "${kernel_version##*___}" SUBDIRS="${PWD}/_kmod_build_${kernel_version%%___*}/${module}"  modules
    done
done


%install
for kernel_version in %{?kernel_versions}; do
    install -d ${RPM_BUILD_ROOT}%{kmodinstdir_prefix}/${kernel_version%%___*}/%{kmodinstdir_postfix}
    install _kmod_build_${kernel_version%%___*}/*/*.ko ${RPM_BUILD_ROOT}%{kmodinstdir_prefix}/${kernel_version%%___*}/%{kmodinstdir_postfix}
done

%{?akmod_install}


%check
# If we built modules, check if it was everything the kmodsrc package provided
MODS=$(find $(ls -d $RPM_BUILD_ROOT%{_prefix}/lib/modules/* |head -n1) -name '*.ko' -exec basename '{}' \; |wc -l)
DIRS=$(ls %{name}-%{version} |wc -l)
[ $MODS = $DIRS ] || [ $MODS = 0 ]


%changelog
* Thu May 15 2014 Nicolas Chauvet <kwizart@gmail.com> - 4.3.10-1.7
- Rebuilt for kernel

* Thu May 08 2014 Nicolas Chauvet <kwizart@gmail.com> - 4.3.10-1.6
- Rebuilt for kernel

* Wed Apr 30 2014 Nicolas Chauvet <kwizart@gmail.com> - 4.3.10-1.5
- Rebuilt for kernel

* Sat Apr 26 2014 Nicolas Chauvet <kwizart@gmail.com> - 4.3.10-1.4
- Rebuilt for kernel

* Wed Apr 16 2014 Nicolas Chauvet <kwizart@gmail.com> - 4.3.10-1.3
- Rebuilt for kernel

* Fri Apr 04 2014 Nicolas Chauvet <kwizart@gmail.com> - 4.3.10-1.2
- Rebuilt for kernel

* Wed Apr 02 2014 Nicolas Chauvet <kwizart@gmail.com> - 4.3.10-1.1
- Rebuilt for kernel

* Mon Mar 31 2014 Sérgio Basto <sergio@serjux.com> - 4.3.10-1
- New upstream release and build also akmods

* Tue Mar 25 2014 Nicolas Chauvet <kwizart@gmail.com> - 4.3.6-2.13
- Rebuilt for kernel

* Sun Mar 09 2014 Nicolas Chauvet <kwizart@gmail.com> - 4.3.6-2.12
- Rebuilt for kernel

* Tue Mar 04 2014 Nicolas Chauvet <kwizart@gmail.com> - 4.3.6-2.11
- Rebuilt for kernel

* Tue Feb 25 2014 Nicolas Chauvet <kwizart@gmail.com> - 4.3.6-2.10
- Rebuilt for kernel

* Mon Feb 24 2014 Nicolas Chauvet <kwizart@gmail.com> - 4.3.6-2.9
- Rebuilt for kernel

* Mon Feb 17 2014 Nicolas Chauvet <kwizart@gmail.com> - 4.3.6-2.8
- Rebuilt for kernel

* Sat Feb 15 2014 Nicolas Chauvet <kwizart@gmail.com> - 4.3.6-2.7
- Rebuilt for kernel

* Wed Feb 12 2014 Nicolas Chauvet <kwizart@gmail.com> - 4.3.6-2.6
- Rebuilt for kernel

* Fri Feb 07 2014 Nicolas Chauvet <kwizart@gmail.com> - 4.3.6-2.5
- Rebuilt for kernel

* Thu Jan 30 2014 Nicolas Chauvet <kwizart@gmail.com> - 4.3.6-2.4
- Rebuilt for kernel

* Tue Jan 28 2014 Nicolas Chauvet <kwizart@gmail.com> - 4.3.6-2.3
- Rebuilt for kernel

* Fri Jan 17 2014 Nicolas Chauvet <kwizart@gmail.com> - 4.3.6-2.2
- Rebuilt for kernel

* Sun Jan 12 2014 Nicolas Chauvet <kwizart@gmail.com> - 4.3.6-2.1
- Rebuilt for kernel

* Thu Dec 26 2013 Sérgio Basto <sergio@serjux.com> - 4.3.6-2
- Rebuild for newer VirtualBox-kmodsrc and build akmods.

* Wed Dec 25 2013 Nicolas Chauvet <kwizart@gmail.com> - 4.3.6-1.2
- Rebuilt for kernel

* Fri Dec 20 2013 Nicolas Chauvet <kwizart@gmail.com> - 4.3.6-1.1
- Rebuilt for kernel

* Thu Dec 19 2013 Sérgio Basto <sergio@serjux.com> - 4.3.6-1
- New upstream release.

* Tue Dec 10 2013 Nicolas Chauvet <kwizart@gmail.com> - 4.3.4-4
- Rebuilt for f20 final kernel

* Sat Dec 07 2013 Nicolas Chauvet <kwizart@gmail.com> - 4.3.4-3
- Rebuilt for f20 final kernel

* Sat Nov 30 2013 Sérgio Basto <sergio@serjux.com> - 4.3.4-1
- New upstream release.

* Sat Nov 02 2013 Sérgio Basto <sergio@serjux.com> - 4.3.2-1
- New upstream release.

* Wed Oct 30 2013 Sérgio Basto <sergio@serjux.com> - 4.3.0-2
- Don't disable hardening which create /dev/vboxdrvu .

* Mon Oct 28 2013 Sérgio Basto <sergio@serjux.com> - 4.3.0-1
- New upstream release.

* Sun Sep 29 2013 Sérgio Basto <sergio@serjux.com> - 4.2.18-2
- Build with patch Additions/linux: fix shared folders for Linux 3.11

* Thu Sep 26 2013 Sérgio Basto <sergio@serjux.com> - 4.2.18-1
- New upstream release.

* Sun Sep 01 2013 Sérgio Basto <sergio@serjux.com> - 4.2.16-2
- Build akmods with src patched for kernel 3.11

* Sat Jul 06 2013 Sérgio Basto <sergio@serjux.com> - 4.2.16-1
- New upstream release.

* Sat Jun 29 2013 Sérgio Basto <sergio@serjux.com> - 4.2.14-1
- New upstream release.

* Mon Apr 15 2013 Sérgio Basto <sergio@serjux.com> - 4.2.12-1
- New upstream release.

* Sat Mar 16 2013 Sérgio Basto <sergio@serjux.com> - 4.2.10-1
- New upstream release.

* Sat Mar 02 2013 Sérgio Basto <sergio@serjux.com> - 4.2.8-1
- New upstream release.

* Tue Dec 25 2012 Sérgio Basto <sergio@serjux.com> - 4.2.6-1
- New upstream release.

* Sun Sep 23 2012 Sérgio Basto <sergio@serjux.com> - 4.2.0-2
- Build with newest VirtualBox-kmodsrc (4.2.0-3).

* Sat Sep 15 2012 Sérgio Basto <sergio@serjux.com> - 4.2.0-1
- 4.2.0 released

* Sun Sep 09 2012 Sérgio Basto <sergio@serjux.com> - 4.2.0-0.2.RC4
- New RC4
- Force use VirtualBox-kmodsrc >= 4.2.0-0.6

* Sat Sep 01 2012 Sérgio Basto <sergio@serjux.com> - 4.2.0-0.1.RC3
- New RC major upstream release.

* Thu Jun 21 2012 Sérgio Basto <sergio@serjux.com> - 4.1.18-1
- New upstream release.

* Wed Jun 13 2012 Sérgio Basto <sergio@serjux.com> - 4.1.16-2
- build with patches to kernels 3.5

* Wed May 23 2012 Sérgio Basto <sergio@serjux.com> - 4.1.16-1
- New upstream release.

* Sat May 19 2012 Sérgio Basto <sergio@serjux.com> - 4.1.14-4
- Bump a release.

* Fri May 18 2012 Sérgio Basto <sergio@serjux.com> - 4.1.14-3
- Rename to VirtualBox-kmod

* Mon May 07 2012 Sérgio Basto <sergio@serjux.com> - 4.1.14-2
- A little review.

* Fri Apr 27 2012 Sérgio Basto <sergio@serjux.com> - 4.1.14-1
- New release.

* Tue Apr 17 2012 Nicolas Chauvet <kwizart@gmail.com> - 4.1.12-3
- Update for UsrMove

* Mon Apr 16 2012 Nicolas Chauvet <kwizart@gmail.com> - 4.1.12-2.2
- rebuild for updated kernel

* Fri Apr 13 2012 Sérgio Basto <sergio@serjux.com> - 4.1.12-2.1
- Just build akmods

* Fri Apr 13 2012 Sérgio Basto <sergio@serjux.com> - 4.1.12-1.1
- New release

* Thu Apr 12 2012 Nicolas Chauvet <kwizart@gmail.com> - 4.1.8-1.3
- rebuild for beta kernel

* Tue Feb 07 2012 Nicolas Chauvet <kwizart@gmail.com> - 4.1.8-1.2
- Rebuild for UsrMove

* Fri Dec 23 2011 Sérgio Basto <sergio@serjux.com> - 4.1.8-1
- New release.

* Sun Dec 11 2011 Sérgio Basto <sergio@serjux.com> - 4.1.6-2
- rebuild for update kmodsrc. 

* Sat Dec 3 2011 Sérgio Basto <sergio@serjux.com> - 4.1.6-1
- Build for new release
- added time package to AkmodsBuildRequires
- removed clean section

* Wed Nov 02 2011 Nicolas Chauvet <kwizart@gmail.com> - 4.1.2-1.4
- Rebuild for F-16 kernel

* Tue Nov 01 2011 Nicolas Chauvet <kwizart@gmail.com> - 4.1.2-1.3
- Rebuild for F-16 kernel

* Fri Oct 28 2011 Nicolas Chauvet <kwizart@gmail.com> - 4.1.2-1.2
- Rebuild for F-16 kernel

* Sun Oct 23 2011 Nicolas Chauvet <kwizart@gmail.com> - 4.1.2-1.1
- Rebuild for F-16 kernel

* Thu Sep 22 2011 Lubomir Rintel <lkundrak@v3.sk> - 4.1.2-1
- New release
- Added vboxpci

* Sat May 28 2011 Thorsten Leemhuis <fedora [AT] leemhuis [DOT] info> - 4.0.4-2
- rebuild for F15 release kernel

* Mon Apr 04 2011 Lubomir Rintel <lkundrak@v3.sk> - 4.0.4-1
- New release

* Mon Feb 14 2011 Lubomir Rintel <lkundrak@v3.sk> - 4.0.2-2
- Fix module symbol versioning

* Sat Feb 05 2011 Lubomir Rintel <lkundrak@v3.sk> - 4.0.2-1
- New release

* Tue Jan 11 2011 Lubomir Rintel <lkundrak@v3.sk> - 3.2.10-2
- Fix build with 2.6.37

* Tue Nov 16 2010 Lubomir Rintel <lkundrak@v3.sk> - 3.2.10-1
- New release

* Mon Jul 12 2010 Lubomir Rintel <lkundrak@v3.sk> - 3.2.6-1
- New release

* Fri Jun 18 2010 Lubomir Rintel <lkundrak@v3.sk> - 3.2.4-1
- New release

* Mon May 10 2010 Lubomir Rintel <lkundrak@v3.sk> - 3.2.0-1
- Release

* Mon May 10 2010 Lubomir Rintel <lkundrak@v3.sk> - 3.2.0-0.2.beta2
- Beta 2

* Thu Apr 29 2010 Lubomir Rintel <lkundrak@v3.sk> - 3.2.0-0.1.beta1
- Beta

* Fri Mar 26 2010 Lubomir Rintel <lkundrak@v3.sk> - 3.1.6-1
- New release

* Wed Feb 17 2010 Lubomir Rintel <lkundrak@v3.sk> - 3.1.4-1
- New release

* Tue Jan 26 2010 Lubomir Rintel <lkundrak@v3.sk> - 3.1.2-1
- New release

* Sun Dec 06 2009 Lubomir Rintel <lkundrak@v3.sk> - 3.1.0-1
- stable

* Tue Nov 24 2009 Lubomir Rintel <lkundrak@v3.sk> - 3.1.0-0.1.beta2
- Bump to beta2

* Thu Nov 12 2009 Lubomir Rintel <lkundrak@v3.sk> - 3.1.0-0.1.beta1
- Bump to beta

* Sun Nov 01 2009 Lubomir Rintel <lkundrak@v3.sk> - 3.0.10-1
- Version bump

* Wed Oct 07 2009 Lubomir Rintel <lkundrak@v3.sk> - 3.0.8-1
- Version bump

* Mon Aug 17 2009 Lubomir Rintel <lkundrak@v3.sk> - 3.0.6-1
- Update to 3.0.6, re-enable hardening

* Mon Aug 17 2009 Lubomir Rintel <lkundrak@v3.sk> - 3.0.4-4
- Source package is now xz-compressed

* Sat Aug 15 2009 Lubomir Rintel <lkundrak@v3.sk> - 3.0.4-2
- Make it possible to disable hardening, do so by default

* Sun Aug 09 2009 Lubomir Rintel <lkundrak@v3.sk> - 3.0.4-1
- New release
- Check that we build all modules present

* Tue Aug 04 2009 Lubomir Rintel <lkundrak@v3.sk> - 3.0.2-2
- Add netadp bmodule (Vlastimil Holer, #744)

* Sun Jul 12 2009 Jonathan Dieter <jdieter@gmail.com> - 3.0.2-1
- New release

* Fri Jul 03 2009 Jonathan Dieter <jdieter@gmail.com> - 3.0.0-1
- New release

* Thu Jul 02 2009 Lubomir Rintel <lkundrak@v3.sk> - 2.2.4-2
- Enable the DRM module

* Fri Jun 05 2009 Thorsten Leemhuis <fedora [AT] leemhuis [DOT] info> - 2.2.4-1.1
- rebuild for final F11 kernel

* Sun May 31 2009 Lubomir Rintel <lkundrak@v3.sk> - 2.2.4-1
- New release

* Sun May 03 2009 Lubomir Rintel <lkundrak@v3.sk> - 2.2.2-1
- New release

* Sat Apr 25 2009 Lubomir Rintel <lkundrak@v3.sk> - 2.2.0-1
- New release

* Fri Apr 24 2009 Lubomir Rintel <lkundrak@v3.sk> - 2.1.4-2
- Fix akmod requires

* Sat Mar 14 2009 Lubomir Rintel <lkundrak@v3.sk> - 2.1.4-1
- Update to 2.1.4
- Enable VBOX_USE_INSERT_PAGE (VirtualBox #3403)
- Use packed source code tarball

* Sat Jan 24 2009 Lubomir Rintel <lkundrak@v3.sk> - 2.1.2-1
- Update to 2.1.2

* Sun Jan 11 2009 Thorsten Leemhuis <fedora [AT] leemhuis [DOT] info> - 2.1.0-2
- Cosmetic fixes
- Fix build of standalone akmod

* Tue Dec 30 2008 Lubomir Rintel <lkundrak@v3.sk> - 2.1.0-1
- New upstream version

* Tue Sep 02 2008 Lubomir Rintel <lkundrak@v3.sk> - 1.6.4-2
- Use the VirtualBox-OSE build-time generated source tree

* Tue Sep 02 2008 Lubomir Rintel <lkundrak@v3.sk> - 1.6.4-1
- New upstream version, don't build for Xen needlessly

* Sat Mar 08 2008 Till Maas <opensource till name> - 1.5.6-3
- rewrite to a kmodspec for rpmfusion

* Fri Mar 07 2008 Lubomir Kundrak <lkundrak@redhat.com> - 1.5.6-2
- Fix build by passing kernel source tree path to make

* Sun Feb 24 2008 Till Maas <opensource till name> - 1.5.6-1
- update to new version

* Sun Jan 20 2008 Till Maas <opensource till name> - 1.5.4-1
- initial spec, split out from VirtualBox-OSE spec
