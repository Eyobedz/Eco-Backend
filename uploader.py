import cloudinary
import cloudinary.uploader
# from cloudinary.utils import cloudinary_url

# Configuration       
cloudinary.config( 
    cloud_name = "dpcgdcpr5", 
    api_key = "688467375666859", 
    api_secret = "1Rgut8ijTC9bUrqLLb8wg-zwQtY", # Click 'View API Keys' above to copy your API secret
    secure=True
)

# Upload an image
upload_result = cloudinary.uploader.upload("uploads/meh.png")
# print(upload_result["secure_url"])
print(upload_result)


# # Optimize delivery by resizing and applying auto-format and auto-quality
# optimize_url, _ = cloudinary_url("shoes", fetch_format="auto", quality="auto")
# print(optimize_url)

# # Transform the image: auto-crop to square aspect_ratio
# auto_crop_url, _ = cloudinary_url("shoes", width=500, height=500, crop="auto", gravity="auto")
# print(auto_crop_url)