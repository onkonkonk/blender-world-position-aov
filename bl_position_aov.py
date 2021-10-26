"""

Blender Position AOV
- Adds World Positon AOV to every Material and enables AOV in all View Layers.

2021-10-26, David Kaiser

"""

import bpy

aov_label = "World Position AOV"

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
