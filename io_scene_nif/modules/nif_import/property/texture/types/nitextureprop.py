"""This modules contains helper methods to import nitexturepropery based texture."""

# ***** BEGIN LICENSE BLOCK *****
#
# Copyright © 2020, NIF File Format Library and Tools contributors.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# * Redistributions of source code must retain the above copyright
#   notice, this list of conditions and the following disclaimer.
#
# * Redistributions in binary form must reproduce the above
#   copyright notice, this list of conditions and the following
#   disclaimer in the documentation and/or other materials provided
#   with the distribution.
#
# * Neither the name of the NIF File Format Library and Tools
#   project nor the names of its contributors may be used to endorse
#   or promote products derived from this software without specific
#   prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
#
# ***** END LICENSE BLOCK *****

from io_scene_nif.modules.nif_import.property.texture import TextureSlotManager
from io_scene_nif.utils.util_logging import NifLog


class NiTextureProp(TextureSlotManager):

    __instance = None

    @staticmethod
    def get():
        """ Static access method. """
        if NiTextureProp.__instance is None:
            NiTextureProp()
        return NiTextureProp.__instance

    def __init__(self):
        """ Virtually private constructor. """
        if NiTextureProp.__instance is not None:
            raise Exception("This class is a singleton!")
        else:
            super().__init__()
            NiTextureProp.__instance = self
            # todo [texture] merge with export slots dict, or change to simple list?
            self.slots = {
                "Base": None,
                "Dark": None,
                "Detail": None,
                "Gloss": None,
                "Glow": None,
                "Bump Map": None,
                "Decal 0": None,
                "Decal 1": None,
                "Decal 2": None,
                # extra shader stuff?
                "Specular": None,
                "Normal": None,
            }

    def import_nitextureprop_textures(self, b_mat, n_texture_desc):
        # NifLog.debug("Importing {0}".format(n_texture_desc))
        self.b_mat = b_mat
        self.clear_default_nodes()
        # go over all valid texture slots
        for slot_name, _ in self.slots.items():
            # get the field name used by nif xml for this texture
            slot_lower = slot_name.lower().replace(' ', '_')
            field_name = f"{slot_lower}_texture"
            # get the tex desc link
            has_tex = getattr(n_texture_desc, "has_"+field_name, None)
            if has_tex:
                NifLog.debug(f"Texdesc has active {slot_name}")
                n_tex = getattr(n_texture_desc, field_name)
                import_func_name = f"link_{slot_lower}_node"
                import_func = getattr(self, import_func_name, None)
                if not import_func:
                    NifLog.debug(f"Could not find linking function {import_func_name} for {slot_name}")
                    continue
                b_texture = self.create_texture_slot(b_mat, n_tex)
                import_func(b_texture)

    def _import_apply_mode(self, n_texture_desc, b_texture):
        # Blend mode
        if hasattr(n_texture_desc, "apply_mode"):
            b_texture.blend_type = self.get_b_blend_type_from_n_apply_mode(n_texture_desc.apply_mode)
        else:
            b_texture.blend_type = "MIX"
