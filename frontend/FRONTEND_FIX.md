# Frontend Fix Guide

## Issue
Next.js can't resolve `@/components/EmissionForm` imports

## Solution

1. **Restart Next.js dev server** (Ctrl+C, then `npm run dev` again)
   - Next.js sometimes needs a restart after creating new files

2. **Clear Next.js cache** (if restart doesn't work):
   ```bash
   rm -rf .next
   npm run dev
   ```

3. **Verify file structure**:
   ```
   frontend/src/
   ├── app/
   │   ├── page.tsx
   │   ├── layout.tsx
   │   └── globals.css
   ├── components/
   │   ├── EmissionForm.tsx
   │   └── ResultsDisplay.tsx
   └── services/
       └── api.ts
   ```

4. **Check tsconfig.json**:
   - Path alias `@/*` should point to `./src/*`
   - Already configured correctly

## Files Created

✅ `tsconfig.json` - TypeScript configuration with path aliases
✅ `postcss.config.js` - PostCSS configuration for Tailwind
✅ `.eslintrc.json` - ESLint configuration

## Next Steps

1. Stop the dev server (Ctrl+C)
2. Restart: `npm run dev`
3. Should work now!

