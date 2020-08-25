# Copyright 2013-2020 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack import *


class Enzo(MakefilePackage):
    """Enzo is a community-developed adaptive mesh refinement simulation code,
    designed for rich, multi-physics hydrodynamic astrophysical calculations.

    To run tests following external tools are needed: yt, matplotlib, git-python and girder-client.
    On Ubuntu it can be installed as
        sudo apt install  python3-yt python3-matplotlib python3-numpy python3-nose python3-git
        sudo pip3 install girder-client
    """

    homepage = "https://enzo-project.org/"
    url      = "https://github.com/enzo-project/enzo-dev/archive/enzo-2.6.1.tar.gz"
    git      = "https://github.com/enzo-project/enzo-dev.git"

    version('develop', branch='master')
    version('2.6.1', sha256='280270accfc1ddb60e92cc98ca538a3e5787e8cc93ed58fb5c3ab75db8c4b048')

    # maintainers = ['github_user1', 'github_user2']

    depends_on('automake', type='build')
    depends_on('mpi')
    depends_on('hdf5')

    variant(
        'opt', default='debug', description='Optimization',
        values=('warn', 'debug', 'cudadebug', 'high', 'aggressive'), multi=False
    )

    # CONFIG_OPT  [opt-{warn,debug,cudadebug,high,aggressive}]  : debug

    # 10.2.0 does not build
    conflicts('%gcc', when='@10.2.0', msg='Enzo cannot be built with gcc@10.2.0')

    def edit(self, spec, prefix):
        configure()
        with working_dir('src/enzo'):
            makefile = FileFilter('Make.mach.linux-gnu')

            # Use the Spack compiler wrappers
            makefile.filter('LOCAL_HDF5_INSTALL\s*=.*',
                            'LOCAL_HDF5_INSTALL    = ' + spec['hdf5'].prefix)
            makefile.filter('LOCAL_INCLUDES_HDF5\s*=.*',
                            'LOCAL_INCLUDES_HDF5   = -I' + spec['hdf5'].prefix.include)

            make('machine-linux-gnu')
            # update option for example set high optimization instead of debug
            #spec['gcc'].
            # gcc-9.3.0 didn't work good make('opt-high')
            make('opt-' + self.spec.variants['opt'].value)

            if self.run_tests is True:
                make('testing-yes')
            # CONFIG_TESTING  [testing-{yes,no}]                        : no
            # check config
            make('show-config')

    def build(self, spec, prefix):
        with working_dir(join_path('src', 'enzo')):
            make()
        with working_dir(join_path('src', 'ring')):
            make()
        with working_dir(join_path('src', 'inits')):
            make()

    def install(self, spec, prefix):
        install_tree('bin', prefix.bin)

        with working_dir(join_path('src', 'ring')):
            install('ring.exe', join_path(prefix.bin, 'ring'))
