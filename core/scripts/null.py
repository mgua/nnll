import os
import logging
from nget import logger, logging, sys_cap
from nget import  contents as config

optimize = config.node_tuner

log_level = getattr(logging, "INFO")
logger = logging.getLogger(__name__)

logger.info("\nAnalyzing model & system capacity\n  Please wait...")


log_level = "INFO"
msg_init = None

logger.info(f"Ready.")
name_path = input("""
Please type the file of an available checkpoint.
Path will be detected.
(default:vividpdxl_realVAE.safetensors):""" or "vividpdxl_realVAE.safetensors")

name_path = os.path.basename(name_path)
diffusion_index = config.get_default("index","DIF")
name_path = name_path.strip()
name_path = os.path.basename(name_path)
if ".safetensors" not in name_path:
     name_path = name_path + ".safetensors"
for key,val in diffusion_index.items():
    if name_path in key:
        model = key
        pass

defaults = optimize.determine_tuning(model)
defaults["generate_image"]["width"] = 832
defaults["generate_image"]["height"] = 1152
defaults["diffusion_prompt"]["batch"] = 1

#pipe = nodes.empty_cache(transformer_models, lora_pipe, unet_pipe, vae_pipe)

device = nodes.force_device(**defaults.get("force_device"))
queue = nodes.diffusion_prompt(**defaults.get("diffusion_prompt"))
if defaults.get("load_transformer",0) != 0: tokenizers, text_encoders = nodes.load_transformer(**defaults.get("load_transformer"))
if defaults.get("encode_prompt",0) != 0: queue = nodes.encode_prompt(**defaults.get("encode_prompt"), queue=queue, tokenizers_in=tokenizers, text_encoders_in=text_encoders,)
if defaults.get("load_vae_model",0) != 0: vae = nodes.load_vae_model(**defaults.get("load_vae_model"))
pipe = nodes.diffusion_pipe(**defaults.get("diffusion_pipe"), vae=vae)
if defaults.get("load_lora",0) != 0: pipe = nodes.load_lora(**defaults.get("load_lora"), pipe=pipe)
pipe = nodes.load_scheduler(**defaults.get("noise_scheduler"), pipe=pipe)
pipe, latent = nodes.generate_image(**defaults.get("generate_image"), pipe=pipe, queue=queue)
if defaults.get("autodecode",0) != 0: image = nodes.autodecode(**defaults.get("autodecode"), pipe=pipe, latent=latent)