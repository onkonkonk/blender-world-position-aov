bl_info = {
    "name": "World Position AOV",
    "author": "David Kaiser, <hello@davidkaiser.net>",
    "version": (0, 1),
    "blender": (2, 93, 3),
    "category": "View Layer",
    "location": "View Layer Properties > Passes",
    "description": "Add World Position AOV",
    "warning": "",
    "doc_url": "",
    "tracker_url": "",
}


import bpy

aov_label = "World Position AOV"

class SCENE_OT_positionAOV(bpy.types.Operator):
    """Adds World Position AOV (Y-up) to all materials and and enables it in view layers"""
    bl_idname = "scene.position_aov"
    bl_label = "World Position AOV"
    bl_options = {'REGISTER', 'UNDO'}
    

    
    def execute(self, context):
        
        
        
        # CREATE NODE GROUP IF NOT ALREADY PRESENT.
        aov_exists = bpy.data.node_groups.get(aov_label)
    
        if not aov_exists:
            
            bpy.data.node_groups.new(aov_label, "ShaderNodeTree")
            bpy.data.node_groups[aov_label].use_fake_user = True
                
            aov_group = bpy.data.node_groups[aov_label]
                

            aov_group.nodes.new("ShaderNodeOutputAOV").label = aov_label
            aov_output = aov_group.nodes["AOV Output"]
            aov_output.name = "P"

            aov_group.nodes.new("ShaderNodeNewGeometry")
            aov_group_input = aov_group.nodes["Geometry"]
                
            aov_group.nodes.new("ShaderNodeSeparateXYZ")
            aov_group_split = aov_group.nodes["Separate XYZ"]

                
            aov_group.nodes.new("ShaderNodeCombineXYZ")
            aov_group_combine = aov_group.nodes["Combine XYZ"]


            # Link Position Pass to Separate XYZ
            aov_group.links.new(aov_group_split.inputs["Vector"], aov_group_input.outputs["Position"])
                
            # Switch Y/Z axis
            aov_group.links.new(aov_group_combine.inputs["X"], aov_group_split.outputs["X"])
            aov_group.links.new(aov_group_combine.inputs["Z"], aov_group_split.outputs["Y"])
            aov_group.links.new(aov_group_combine.inputs["Y"], aov_group_split.outputs["Z"])
                
            # Link Combine XYZ to Output
            aov_group.links.new(aov_output.inputs["Color"], aov_group_combine.outputs["Vector"])


        # ADD NODE GROUP TO ALL MATERIALS IF NOT ALREADY PRESENT.
        for i in bpy.data.materials.items():
            current_mat = bpy.data.materials[str(i[0])]
            current_mat.use_nodes = True

            group_exists = current_mat.node_tree.nodes.get(aov_label)

            if not group_exists:
                current_mat.node_tree.nodes.new("ShaderNodeGroup").name = aov_label
                current_mat.node_tree.nodes[aov_label].node_tree = bpy.data.node_groups[aov_label]

        # ADD SHADER AOV IN RENDER PASSES FOR EACH VIEW LAYER.
        aov_pass_name = bpy.data.node_groups[aov_label].nodes["AOV Output"].name
            
        s = bpy.data.scenes.values()

        for n in range(0, len(s)):
            current_scene = s[n]
            v = s[n].view_layers.items()
                
            for j in range(0, len(v)):
                current_layer = s[n].view_layers[j]
                pass_exists = current_layer.aovs.get(aov_pass_name)

                if not pass_exists:
                    current_layer.aovs.add().name = aov_pass_name

        return {'FINISHED'}

class SCENE_PT_positionAOV(bpy.types.Panel):
    bl_label = "World Position"
    bl_idname = "SCENE_PT_position_aov"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "view_layer"
    bl_parent_id = "VIEWLAYER_PT_layer_passes"
    

    
    def draw(self, context):
        button_text = "Create "
        if bpy.data.node_groups.get(aov_label):
            button_text = "Update "
        
        self.layout.operator('scene.position_aov', text=button_text + 'World Position AOV' )



def register():
    bpy.utils.register_class(SCENE_OT_positionAOV)
    bpy.utils.register_class(SCENE_PT_positionAOV)

def unregister():
    bpy.utils.unregister_class(SCENE_OT_positionAOV)
    bpy.utils.unregister_class(SCENE_PT_positionAOV)
    

if __name__ == "__main__":
    register()


