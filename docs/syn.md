## Programming by demonstration (PBD)

### Web trace collection
- We record XPATH or CSS. 
- If users do "Ctrl+C" when hovering over an element, we mark and save it; If users press tab, then the plugin should automatically infer other similar items on the page (and let users unselect unwanted items). 

### Desktop PBD
- Mouse: record mouse clicks using mouse position. this would suffer from the loading time variance issues (e.g., a button takes longer to load). So it is best to use OCR or cropped image to locate when doing desktop PBD

- How to locate? Ideally our tool should save the image when the click happens. However, this is not like web PBD where we have XPTHA/CSS selector; we still need some hints from users to get the correct information. E.g., we ask users to circle the region of interest before clicking.

```yaml
- os.record(macro-open-game, {{ { 
    'start':'Enter+Enter',
    'end':'Esc+Esc',
    'mode':'text|icon'} }})
```

- [GUI icon detection (ML)](https://asiffer.github.io/posts/desktop-elements-detection-using-deep-learning/). Fast RCNN or Yolo to detect the bounding box and classification. May suffer from limited generalization.

- [Conventional CV-based solution](https://github.com/tezansahu/smart_ui_tf20/blob/main/app/app.py#L136). 

```python
options["cnn_model"] ="CNN (Wireframes & ReDraw)"
options["min_grad"] = 3 # 1-10
options["ffl_block"] = 5 # 1-10
options["min_ele_area"] = 25 # 10-200
options["merge_contained_ele"] = False
```

```shell
python run_single.py --img /Users/hecmay/Desktop/temp.png --op_dir ./ --min_grad 3 --ffl_block 5 --min_ele_area 25 --max_word_inline_gap 4 --max_line_gap 4
```