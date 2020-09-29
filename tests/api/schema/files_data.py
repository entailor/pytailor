files_schema_ex1 = {
  "in": {
    "coordfile": {
      "ext": ["txt"],
      "title": "Coordinates",
      "description": "A file with coordinate values of nodes",
      "required": True
    },
    "test": {
      "ext": ["pdf", "dat"],
      "multiple": True,
      "title": "Test",
      "description": "Just a test"}}}

files_ex1 = {
    'tag': 'coordfile',
    "ext": ["txt"],
}
files_ex2 = {
    'tag': 'coordfile',
    "ext": ["txt"],
    "title": "Coordinates",
    "multiple": True,
    "description": "A file with coordinate values of nodes",
    "required": True
}
files_ex3 = {
    'tags': ['coordfile', 'datfile'],
    "exts": [["txt"], ["txt"]],
}
