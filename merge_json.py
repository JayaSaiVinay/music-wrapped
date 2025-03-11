import json
with open("StreamingHistory_music_0.json", "r", encoding="utf-8") as file0:
    data0 = json.load(file0)

with open("StreamingHistory_music_1.json", "r", encoding="utf-8") as file1:
    data1 = json.load(file1)

with open("StreamingHistory_music_2.json", "r", encoding="utf-8") as file2:
    data2 = json.load(file2)
# Merge the two lists
merged_data = data0 + data1 + data2

# Save the merged data into a new file
with open("Merged_StreamingHistory.json", "w", encoding="utf-8") as merged_file:
    json.dump(merged_data, merged_file, ensure_ascii=False, indent=4)

print("Files merged successfully!")
