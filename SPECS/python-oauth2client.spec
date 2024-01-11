%global srcname oauth2client
%global sum Python client library for OAuth 2.0
# Share doc between python- and python3-
%global _docdir_fmt %{name}


%if 0%{?fedora} || 0%{?rhel} > 7
%bcond_without python3
%else
%bcond_with python3
%endif

%if 0%{?rhel} < 7
%bcond_without python2
%else
%bcond_with python2
%endif

Name:           python-%{srcname}
Version:        4.1.2
Release:        6%{?dist}
Summary:        %{sum}

Group:          Development/Languages
License:        ASL 2.0
URL:            https://github.com/google/%{srcname}
Source0:        https://github.com/google/%{srcname}/archive/v%{version}.tar.gz#/%{srcname}-%{version}.tar.gz
Patch0:         docs-build-fix.patch
Patch1:         rsa-to-cryptography.patch

BuildArch:      noarch

%if %{with python2}
BuildRequires:  python2-devel
BuildRequires:  pytest
BuildRequires:  python2-setuptools
BuildRequires:  python2-fasteners
BuildRequires:  python2-six >= 1.6.1
%endif

%if 0%{?fedora}
# Needed for docs build
BuildRequires:  pyOpenSSL
BuildRequires:  python-crypto
BuildRequires:  python2-django1.11
BuildRequires:  python-jsonpickle
BuildRequires:  python-flask
BuildRequires:  python2-gflags
BuildRequires:  python-httplib2
BuildRequires:  python-keyring
BuildRequires:  python-mock
BuildRequires:  python-nose
BuildRequires:  python2-pyasn1 >= 0.1.7
BuildRequires:  python2-pyasn1-modules >= 0.0.5
BuildRequires:  python2-cryptography >= 1.7.2
BuildRequires:  python-sqlalchemy
BuildRequires:  python-tox
BuildRequires:  python-unittest2
BuildRequires:  python-webtest
# RHEL 7 has too old a version of python-sphinx
BuildRequires:  python-sphinx > 1.3
BuildRequires:  python-sphinx_rtd_theme
%endif

%if %{with python3}
BuildRequires:  python3-setuptools
BuildRequires:  python3-devel
# For tests only
#BuildRequires:  python3-fasteners
#BuildRequires:  python3-mock
#BuildRequires:  python3-pyasn1 >= 0.1.7
#BuildRequires:  python3-pyasn1-modules >= 0.0.5
#BuildRequires:  python3-tox
#BuildRequires:  python3-pytest
%endif

%description
This is a python client module for accessing resources protected by OAuth 2.0

%if %{with python2}
%package -n python2-%{srcname}
Summary:        %{sum}
%{?python_provide:%python_provide python2-%{srcname}}

Requires:       pyOpenSSL
Requires:       python2-gflags
Requires:       python-httplib2
Requires:       python-keyring
Requires:       python2-pyasn1 >= 0.1.7
Requires:       python2-pyasn1-modules >= 0.0.5
Requires:       python2-cryptography >= 1.7.2
Requires:       python2-fasteners
Requires:       python2-six >= 1.6.1

%description -n python2-%{srcname}
This is a python client module for accessing resources protected by OAuth 2.0
%endif

%if %{with python3}
%package -n python3-%{srcname}
Summary:        %{sum}
%{?python_provide:%python_provide python3-%{srcname}}

Requires:       python3-pyOpenSSL
Requires:       python3-gflags
Requires:       python3-fasteners
Requires:       python3-httplib2 >= 0.9.1
#Requires:       python3-keyring
Requires:       python3-pyasn1 >= 0.1.7
Requires:       python3-pyasn1-modules >= 0.0.5
Requires:       python3-cryptography >= 1.7.2
Requires:       python3-six >= 1.6.1

%description -n python3-%{srcname}
This is a python client module for accessing resources protected by OAuth 2.0
%endif

%if 0%{?fedora}
%package doc
Summary:        Documentation for python oauth2client

%description doc
The python-oauth2client-doc package provides the documentation
for the package. Documentation is shipped in html format.
%endif

%prep
%setup -q -n %{srcname}-%{version}
%patch0 -p1 -b .doc
%patch1 -p1

# Remove the version constraint on httplib2.  From reading upstream's git log,
# it seems the only reason they require a new version is to force python3
# support.  That doesn't affect us on EPEL7, so we can loosen the constraint.
sed -i 's/httplib2>=0.9.1/httplib2/' setup.py

# We do not have the package for google.appengine support
# This is removed because it breaks the docs build otherwise
rm -f docs/source/oauth2client.contrib.appengine.rst oauth2client/appengine.py

%if %{with python2}
rm -rf %{py2dir}
cp -a . %{py2dir}
%endif

%build
%if %{with python3}
%py3_build
%endif

%if 0%{?fedora}
export PYTHONPATH=`pwd`
pushd docs
# Not running with smp_flags as sometimes sphinx fails when run
# with parallel make
make html
popd
unset PYTHONPATH
rm -vr docs/_build/html/_sources
rm -vr docs/_build/html/_static/fonts
rm -v docs/_build/html/{.buildinfo,objects.inv}
%endif

%if %{with python2}
pushd %{py2dir}
%py2_build
%endif

%install
%if %{with python3}
%py3_install
%endif

%if %{with python2}
pushd %{py2dir}
%py2_install
popd
%endif

%check

%if %{with python2}
pushd %{py2dir}
tox -v --sitepackages -e py27
popd
%endif

%if %{with python3}
#python3-tox --sitepackages -e py35
%endif

# We remove tests currently, we will ship them eventually
# This is a bit of a hack until I package the test scripts in a separate package
rm -r $(find %{_buildrootdir} -type d -name 'tests') || /bin/true


%if %{with python2}
%files -n python2-%{srcname}
%license LICENSE
%doc CHANGELOG.md CONTRIBUTING.md README.md 
%{python2_sitelib}/%{srcname}
%{python2_sitelib}/%{srcname}-%{version}-*.egg-info
%endif

%if 0%{?fedora}
%files doc
%doc docs/_build/html
%endif

%if %{with python3}
%files -n python3-%{srcname}
%license LICENSE 
%doc CHANGELOG.md CONTRIBUTING.md README.md 
%{python3_sitelib}/%{srcname}
%{python3_sitelib}/%{srcname}*.egg-info
%endif

%changelog
* Mon Jul 30 2018 Oyvind Albrigtsen <oalbrigt@redhat.com> - 4.1.2-6
- Use FIPS 140-2 compliant RSA library

* Tue Jun 05 2018 Troy Dawson <tdawson@redhat.com> - 4.1.2-5.1
- Do not do python2 in RHEL8

* Wed Mar 21 2018 Michele Baldessari <michele@acksyn.org> - 4.1.2-4
- Fix FTBFS due to missing python-django (rhbz#1556223)
- Set right version in the docs

* Fri Feb 09 2018 Fedora Release Engineering <releng@fedoraproject.org> - 4.1.2-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_28_Mass_Rebuild

* Thu Jul 27 2017 Fedora Release Engineering <releng@fedoraproject.org> - 4.1.2-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Mon Jul 10 2017 Michele Baldessari <michele@acksyn.org> - 4.1.2-1
- New upstream

* Sat May 13 2017 Michele Baldessari <michele@acksyn.org> - 4.1.0-1
- New upstream

* Thu Mar 30 2017 Ralph Bean <rbean@redhat.com> - 4.0.0-2
- Compat for EPEL7.

* Wed Mar 29 2017 Ralph Bean <rbean@redhat.com> - 4.0.0-1
- new version

* Sat Feb 11 2017 Fedora Release Engineering <releng@fedoraproject.org> - 3.0.0-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild

* Tue Dec 27 2016 Michele Baldessari <michele@acksyn.org> - 3.0.0-3
- Fix python 3.6 breakage

* Mon Dec 19 2016 Miro Hrončok <mhroncok@redhat.com> - 3.0.0-2
- Rebuild for Python 3.6

* Thu Nov 10 2016 Michele Baldessari <michele@acksyn.org> - 3.0.0-1
- New upstream

* Tue Jul 19 2016 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.1.0-2
- https://fedoraproject.org/wiki/Changes/Automatic_Provides_for_Python_RPM_Packages

* Sun May 22 2016 Michele Baldessari <michele@acksyn.org> - 2.1.0-1
- New upstream
* Tue Mar 08 2016 Michele Baldessari <michele@acksyn.org> - 2.0.1-1
- New upstream (NB: for now I am not shipping the tests, to be revised later)
* Thu Feb 04 2016 Fedora Release Engineering <releng@fedoraproject.org> - 1.5.2-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild
* Thu Nov 26 2015 Michele Baldessari <michele@acksyn.org> - 1.5.2-2
- Remove dependency on sphinx-contrib-napoleon now that sphinx is at version >= 1.3
- Tighten versioned dependencies
- Update to latest python policy
* Thu Nov 19 2015 Michele Baldessari <michele@acksyn.org> - 1.5.2-1
- New upstream (BZ 1283443)
* Tue Nov 10 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.5.1-3
- Rebuilt for https://fedoraproject.org/wiki/Changes/python3.5
* Tue Oct 13 2015 Michele Baldessari <michele@acksyn.org> - 1.5.1-2
- Add versioned requires as per setup.py
* Thu Sep 17 2015 Michele Baldessari <michele@acksyn.org> - 1.5.1-1
- New upstream (BZ#1263881)
* Fri Sep 04 2015 Michele Baldessari <michele@acksyn.org> - 1.5.0-1
- New upstream (BZ#1259966)
* Sun Jul 12 2015 Michele Baldessari <michele@acksyn.org> - 1.4.12-1
- New upstream (BZ#1241304)
* Mon Jun 22 2015 Michele Baldessari <michele@acksyn.org> - 1.4.11-2
- Use -O1 for python3 as well
- Use python2 macros
- Remove the extra fonts from the -doc package
* Thu Jun 04 2015 Michele Baldessari <michele@acksyn.org> - 1.4.11-1
- Initial packaging
