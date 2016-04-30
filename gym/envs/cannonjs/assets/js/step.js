step({action});
var extractedOutput = queue.dequeue();
extractedOutput = extractedOutput ? extractedOutput : "";
var jsonString = JSON.stringify(extractedOutput);
return jsonString;