# Product Images Directory

## 📸 How to Add Product Images

### Step 1: Save Your Images Here

Place your product images in this folder:
```
frontend/images/
├── macbook-pro-m3.jpg
├── iphone-15-pro-max.jpg
└── your-product-image.jpg
```

### Step 2: Recommended Image Specifications

- **Format**: JPG, PNG, or WebP
- **Size**: 800x800 pixels (or 1:1 aspect ratio)
- **File size**: Under 500KB for fast loading
- **Naming**: Use lowercase with hyphens (e.g., `macbook-pro-m3.jpg`)

### Step 3: Reference in Your Data

When uploading products, use relative paths:

```json
{
  "product_id": "prod_001",
  "name": "MacBook Pro",
  "image": "images/macbook-pro-m3.jpg",
  ...
}
```

## 🌐 Alternative: Using External URLs

You can also use external image URLs:

```json
{
  "image": "https://example.com/product-image.jpg"
}
```

### Free Image Resources:

1. **Unsplash** - https://unsplash.com
   - High-quality free photos
   - No attribution required

2. **Pexels** - https://pexels.com
   - Free stock photos
   - Great product photography

3. **Pixabay** - https://pixabay.com
   - Free images and videos
   - Large selection

4. **Apple Press Kit** (for Apple products)
   - Official product images
   - Check usage rights

## 📝 Example: Getting Images from Unsplash

1. Go to https://unsplash.com
2. Search for "MacBook Pro" or "iPhone 15 Pro"
3. Click on image
4. Right-click → "Copy image address"
5. Use that URL in your product data

## 💡 Tips

- **Local images load faster** than external URLs
- **External URLs** are easier to manage (no file uploads)
- **Optimize images** before adding (compress for web)
- **Use consistent aspect ratios** for better UI

## ⚠️ Important Notes

- Images in this folder are **publicly accessible** when server is running
- The frontend server (`python -m http.server`) automatically serves files from this directory
- Path in database should be relative: `images/your-file.jpg`
- Make sure image file names **match exactly** (case-sensitive)

## 🎨 Image Optimization Tools

- **TinyPNG** - https://tinypng.com (compress images)
- **Squoosh** - https://squoosh.app (Google's image optimizer)
- **ImageOptim** - https://imageoptim.com (Mac app)

---

**Current Setup:**
- MacBook Pro image: `images/macbook-pro-m3.jpg`
- iPhone 15 Pro Max image: `images/iphone-15-pro-max.jpg`

Just add your image files with these exact names and they'll display automatically! 🚀

