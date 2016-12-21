#!/usr/bin/env python
#
# Copyright 2016 Google Inc.
#
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

# Generate Android.bp for Skia from GN configuration.

import json
import os
import pprint
import string
import subprocess
import tempfile

# First we start off with a template for Android.bp,
# with holes for source lists and include directories.
bp = string.Template('''// This file is autogenerated by gn_to_bp.py.

cc_library {
    name: "libskia",
    cflags: [
        "-fexceptions",
        "-Wno-unused-parameter",
        "-U_FORTIFY_SOURCE",
        "-D_FORTIFY_SOURCE=1",
        "-DSKIA_IMPLEMENTATION=1",
    ],

    export_include_dirs: [
        $export_includes
    ],

    local_include_dirs: [
        $local_includes
    ],

    srcs: [
        $srcs
    ],

    arch: {
        arm: {
            srcs: [
                $arm_srcs
            ],

            armv7_a_neon: {
                srcs: [
                    $arm_neon_srcs
                ],
            },
        },

        arm64: {
            srcs: [
                $arm64_srcs
            ],
        },

        mips: {
            srcs: [
                $none_srcs
            ],
        },

        mips64: {
            srcs: [
                $none_srcs
            ],
        },

        x86: {
            srcs: [
                $x86_srcs
            ],
        },

        x86_64: {
            srcs: [
                $x86_srcs
            ],
        },
    },

    shared_libs: [
        "libEGL",
        "libGLESv2",
        "libdng_sdk",
        "libexpat",
        "libft2",
        "libicui18n",
        "libicuuc",
        "libjpeg",
        "liblog",
        "libpiex",
        "libpng",
        "libvulkan",
        "libz",
    ],
    static_libs: [
        "libsfntly",
        "libwebp-decode",
        "libwebp-encode",
    ],
}''')

# We'll run GN to get the main source lists and include directories for Skia.
gn_args = {
  'skia_enable_vulkan_debug_layers': 'false',
  'skia_use_system_expat':           'true',
  'skia_use_vulkan':                 'true',
  'target_cpu':                      '"none"',
  'target_os':                       '"android"',
}
gn_args = ' '.join(sorted('%s=%s' % (k,v) for (k,v) in gn_args.iteritems()))

tmp = tempfile.mkdtemp()
subprocess.check_call(['gn', 'gen', tmp, '--args=%s' % gn_args, '--ide=json'])

js = json.load(open(os.path.join(tmp, 'project.json')))

def strip_slashes(lst):
  return [str(p.lstrip('/')) for p in lst]

srcs            = strip_slashes(js['targets']['//:skia']['sources'])
local_includes  = strip_slashes(js['targets']['//:skia']['include_dirs'])
export_includes = strip_slashes(js['targets']['//:public']['include_dirs'])

# Grab the sources from targets :skia depends on (optional Skia components).
for dep in js['targets']['//:skia']['deps']:
  if 'third_party' in dep:
    continue   # We've handled all third-party DEPS as static or shared_libs.
  if 'none' in dep:
    continue   # We'll handle all cpu-specific sources manually later.
  srcs.extend(strip_slashes(js['targets'][dep].get('sources', [])))

# No need to list headers.
srcs = [s for s in srcs if not s.endswith('.h')]

# Most defines go into SkUserConfig.h, where they're seen by Skia and its users.
# Start with the defines :skia uses, minus a couple.  We'll add more in a bit.
defines = [str(d) for d in js['targets']['//:skia']['defines']]
defines.remove('SKIA_IMPLEMENTATION=1')  # Only libskia should have this define.

# For architecture specific files, it's easier to just read the same source
# that GN does (opts.gni) rather than re-run GN once for each architecture.

# This .gni file we want to read is close enough to Python syntax
# that we can use execfile() if we supply definitions for GN builtins.
# While we're at it, grab defines specific to Android Framework the same way.

def get_path_info(path, kind):
  assert kind == "abspath"
  # While we want absolute paths in GN, relative paths work best here.
  return path

builtins = { 'get_path_info': get_path_info }
defs = {}
here = os.path.dirname(__file__)
execfile(os.path.join(here,                      'opts.gni'), builtins, defs)
execfile(os.path.join(here, 'android_framework_defines.gni'), builtins, defs)

# This should finish off the defines.
defines += defs['android_framework_defines']
defines.extend([
  'GR_GL_CUSTOM_SETUP_HEADER "gl/GrGLConfig_chrome.h"',
  'SKIA_DLL',
  'SK_BUILD_FOR_ANDROID_FRAMEWORK',
  'SK_DEFAULT_FONT_CACHE_LIMIT   (768 * 1024)',
  'SK_DEFAULT_GLOBAL_DISCARDABLE_MEMORY_POOL_SIZE (512 * 1024)',
  'SK_IGNORE_ETC1_SUPPORT',
  'SK_USE_FREETYPE_EMBOLDEN',
])
# TODO: move these all to android_framework_defines.gni?

# Turn paths from opts.gni into paths relative to external/skia.
def scrub(lst):
  # Perform any string substitutions.
  for var in defs:
    if type(defs[var]) is str:
      lst = [ p.replace('$'+var, defs[var]) for p in lst ]
  # Relativize paths to top-level skia/ directory.
  return [os.path.relpath(p, '..') for p in lst]

# Turn a list of strings into the style bpfmt outputs.
def bpfmt(indent, lst):
  return ('\n' + ' '*indent).join('"%s",' % v for v in sorted(lst))

# OK!  We have everything to fill in Android.bp...
with open('Android.bp', 'w') as f:
  print >>f, bp.substitute({
    'export_includes': bpfmt(8, export_includes),
    'local_includes':  bpfmt(8, local_includes),
    'srcs':            bpfmt(8, srcs),

    'arm_srcs':      bpfmt(16, scrub(defs['armv7'])),
    'arm_neon_srcs': bpfmt(20, scrub(defs['neon'])),
    'arm64_srcs':    bpfmt(16, scrub(defs['arm64'] +
                                     defs['crc32'])),
    'none_srcs':     bpfmt(16, scrub(defs['none'])),
    'x86_srcs':      bpfmt(16, scrub(defs['sse2'] +
                                     defs['ssse3'] +
                                     defs['sse41'] +
                                     defs['sse42'] +
                                     defs['avx'  ] +
                                     defs['hsw'  ]))
  })

#... and all the #defines we want to put in SkUserConfig.h.
with open('include/config/SkUserConfig.h', 'w') as f:
  print >>f, '// This file is autogenerated by gn_to_bp.py.'
  print >>f, '#ifndef SkUserConfig_DEFINED'
  print >>f, '#define SkUserConfig_DEFINED'
  for define in sorted(defines):
    print >>f, '  #define', define.replace('=', ' ')
  print >>f, '#endif//SkUserConfig_DEFINED'
