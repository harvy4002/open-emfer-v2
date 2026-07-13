# Technical Research: Camper Profile Status Photos

## Unknowns & Clarifications (from Technical Context)

All previously identified unknowns from the specification phase have been thoroughly researched and resolved.

1. **How does the frontend currently map image URLs to status texts?**
   - *Investigation*: Searched `web/js/app.js` for "camper-status-image".
   - *Discovery*: Currently, line 36 of `app.js` utilizes a hardcoded dictionary (`const STATUS_IMAGES`) mapping PascalCase status tags (e.g. `"Chilling"`, `"Roaming"`, `"Drinking"`) to external `unsplash.com` fallback URLs. At line 195, when the status string is fetched from `/beer?event=status`, it looks up the URL from this dictionary.
   - *Resolution*: We will deprecate this external URL dictionary. Instead, the UI will dynamically construct local paths based on the `activeUser` variable and the `statusText` payload, converting the status text to lowercase (e.g. `/${activeUser}_status/${activeUser}_${statusText.toLowerCase()}.jpg`).

2. **How do we handle missing `.jpg` image files gracefully without breaking the UI?**
   - *Investigation*: Since image URLs will be constructed purely via string interpolation on the client side, if a camper uses a status (e.g. "Hiking") without uploading a `harvy_hiking.jpg` image to the S3 bucket, it will trigger an HTTP 404 (Not Found).
   - *Decision*: We will implement a native HTML `onerror` fallback directly on the `#camper-status-image` DOM element. If the primary dynamically generated JPG URL fails to load, the `onerror` event will seamlessly overwrite the `src` attribute to the universally guaranteed `${activeUser}_normal.jpg` fallback image.

## Technology Choices & Best Practices

1. **Frontend Architecture**
   - **Decision**: Client-side dynamic string interpolation with native HTML `onerror` fallbacks.
   - **Rationale**: Retains the serverless S3/CloudFront simplicity mandated by Constitution Principle VII. It eliminates the need for AWS API Gateway to do heavy server-side checks for file existence before responding.

2. **Image Aspect Ratio Constraints**
   - **Decision**: Enforce CSS `object-fit: cover; max-height: 250px;` on the `#camper-status-image` DOM node container.
   - **Rationale**: Since user-uploaded JPG files may have unpredictable aspect ratios, utilizing `object-fit: cover` ensures the images fill the bounding box securely like a social media profile picture, masking any stretching.
