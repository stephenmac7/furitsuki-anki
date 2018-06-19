# Furitsuki Configuration
- `srcFields : [String]` holds field names readings should be generated for
- `dstFields : [String]` holds field names where generated readings should be placed
- `checkModel : Bool` determines whether the model name should be checked before adding a reading when Bulk-adding
- `models : [String]` a lower-case list of models that *should* have readings added; only applies when `checkModel` is true
- `addOnFocusLost : Bool` Determines whether readings should be added when a field in `srcFields` loses focus. Conflicts with Japanese support addon. 
