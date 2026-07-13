# Data Model: Camper Profile Status Photos

## 1. Domain Entities & URL Routing Structure

The Camper Profile Status feature operates entirely on the client side using string interpolation mapped against standard static web assets hosted on Amazon S3. It introduces no new backend database tables.

### 1.1 Camper Status Image State Machine

The client-side DOM container (`#camper-status-image`) transitions its `src` attribute through the following state machine upon each successful telemetry ping:

| Property | Format / Type | Description / Routing Rule |
| :--- | :--- | :--- |
| `activeUser` | `string` | Extracted from the URL `?u=` parameter (e.g. `hvy`, `cha`). |
| `statusText` | `string` | Extracted from the `/beer?event=status` API JSON response payload (e.g. `Chilling`, `Drinking`). |
| `normalizedStatus` | `string` | The `statusText` mapped strictly to lowercase via `.toLowerCase()`. |
| **Primary Route** | `URL Path` | Constructed as: `/{activeUser}_status/{activeUser}_{normalizedStatus}.jpg` |
| **Fallback Route** | `URL Path` | Constructed as: `/{activeUser}_status/{activeUser}_normal.jpg` |

## 2. Directory Layout Constraints

For the client-side state machine to resolve properly, static files hosted on S3 must strictly adhere to the following normalized layout:

```text
web/
├── hvy_status/
│   ├── hvy_sleeping.jpg
│   ├── hvy_drinking.jpg
│   ├── hvy_normal.jpg (Required fallback)
│   └── hvy_chilling.jpg
├── cha_status/
│   ├── cha_sleeping.jpg
│   ├── cha_coding.jpg
│   └── cha_normal.jpg (Required fallback)
```

## 3. Validation Rules

- **Lowercase Normalization**: Regardless of how status cases are entered manually or stored in DynamoDB (e.g., "Sleeping", "SLEEPING"), they must be rendered as strictly lowercase when mapped to file extensions to maintain predictable UX loading states across all web servers.
- **Max Bounding Size**: The DOM element rendering the image must cap at 250px-300px height. Any image dimensions extending past this ratio will be securely cropped via CSS `object-fit: cover`.
