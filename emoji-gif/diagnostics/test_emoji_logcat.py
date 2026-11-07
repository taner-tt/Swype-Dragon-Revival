from analyze_emoji_logcat import analyze
sample=[
  'E/Swype: loadCodePoints(): called :: arrayType=0',
  'D/Swype: loadCodePoints: called smiley :: added emoji ::  1F600 :: emoji size==0',
  'D/Swype: loadCodePoints: called smiley :: added emoji ::  1F970 :: emoji size==0',
  'D/Swype: loadCodePoints: called smiley :: added emoji ::  1F929 :: emoji size==0',
  'D/Swype: EmojiPageView() setItems : called :: emojis.size() 35 , cells count:: 42 , pageNumber : 0',
  'D/Other: private user message SHOULD NEVER BE EMITTED']
a=analyze(sample)
assert a['target_positions_after_filtering']['1F970'][0]['filtered_ordinal']==2
assert a['target_positions_after_filtering']['1F929'][0]['filtered_ordinal']==3
assert len(a['observed_page_calls'])==1
assert 'private user message' not in str(a)
print('PASS: DEX-derived emoji log records parsed; unrelated input never emitted')
