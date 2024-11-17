# VECTOR SEARCH ON ONPREMISE SQL SERVER
**Summary:**

In this article, you will learn the concept of Vector Search, which is the SQL Server equivalent of the concept of artificial intelligence, which has entered every aspect of our lives, and how I do the vector search process, which is not yet in SQL Server On Prem systems, with the T-SQL codes I wrote. Since the article is quite long, I wanted to write here what you will learn after reading what is explained here. Based on it, you can decide whether you are interested in it or not.

**1.**What is the vector search process and the concept of vector?

**2.**Instead of searching for text in the form _of Select \* from Items where title\_ like ‘Lenovo%laptop%bag%’_  that we know in SQL Server

When it is said _“I am looking for a Lenovo notebook bag”,_ how to search like a prompt?

Or how can the same result be brought when “I am looking for a notebook backpack with Lenovo Brand” is written in a Turkish dataset?

**3.**How to vectorize a text?

**4.**What is cosine distance? How to calculate the similarity of two vectors?

**5.**How to quickly perform a vector search on SQL Server?

**6.** How to use Clustered Columnstore Index and Ordered Clustered Columnstore index for advanced performance?

**7.**How can we create a vector index, which is a feature that is not available in SQL Server.

You can go to github repository here:

Or you can download the database I worked on it here: [VectorDB100K\_EN](https://1drv.ms/f/s!AmI3ms7NfBMm-Trkm6MD2RpKGeeW?e=sv09RH)

**1.Introduction**

The process we do when we search in SQL Server is obvious, right?

For example, let’s say “_Lenovo Notebook Bag”_ is the phrase we searched for.

Here’s how we can call it.

_SELECT \* FROM WEBITEMS WHERE TITLE\_ LIKE ‘%LENOVO NOTEBOOK BAG%’_

We see that there is no result from this, because there is no product in which these three words are neighboor to each other.

![](https://omercolakoglu.net/wp-content/uploads/2024/11/image-1.png?w=945)

In this case, these three words can be mentioned in separate places, but we can write them as follows with the logic that they should be in the same sentence.

`SELECT ID, DESCRIPTION_ FROM WEBITEMS WHERE   DESCRIPTION_ LIKE N'%Lenovo%'   AND DESCRIPTION_ LIKE N'%Notebook%'   AND DESCRIPTION_ LIKE N'%Bag%'`

As you can see, here are some records that fit this format.

![](https://omercolakoglu.net/wp-content/uploads/2024/11/image-2.png?w=945)

Another alternative method is to perform this search with the fulltext search search operation.

```SQL
SELECT ID,DESCRIPTION_EN  FROM WEBITEMS WHERE
CONTAINS(DESCRIPTION_EN,N'Lenovo')
AND CONTAINS(DESCRIPTION_EN,N'Notebook')
AND CONTAINS(DESCRIPTION_EN,N'Bag')
```

![](https://omercolakoglu.net/wp-content/uploads/2024/11/image-3.png?w=945)
Of course, the fulltext search process is a structure that works very, very fast compared to others.
Now we have gone over our existing knowledge so far.

**2.Vector search operation and vector concept**
Now I’m going to introduce you to a new concept. **“Vector Search”**
Especially after concepts such as GPTs, language models, artificial intelligence came out, the rules of the game changed considerably. We now do a lot of our work by writing prompts. Because artificial intelligence is smart enough to understand what we want with the prompt.
So what’s going on on the SQL Server side at this point?
There are also the concepts of Vector Store and Vector Search.
Basically, here’s the thing.
It converts a text expression into a vector array of a certain length (I used it here with 1536 elements) and keeps the data that way.
The vector here consists of 1536 floats.
We convert all the lines of a column that we keep as text in the table to vector and store them as vectors inside, and when we want to search, we convert the text expression we want to search into vectors and calculate the similarity between these two vectors for all rows and try to find the closest one.
For example, let’s say the sentence we want to search for.
_“I am looking for a Lenovo or Samsonite notebook bag.”_
When we convert this to vector, we get the following result.

```SQL
DECLARE @STR AS NVARCHAR(MAX);
SET @STR = 'I am looking for a Lenovo or Samsonite notebook bag.'
DECLARE @VECTOR AS NVARCHAR(MAX);
EXEC GENERATE_EMBEDDINGS @STR, @VECTOR OUTPUT;
SELECT @VECTOR AS VECTOR1536;
```
![](https://omercolakoglu.net/wp-content/uploads/2024/11/image-4.png?w=945)
_“I am looking for a Lenovo or Samsonite notebook bag.”_
**Vectorized (embedded) of the expression**:
_\-0.011496219,-0.0037424976,0.010762138,-0.013167562,-0.015284596,0.016097328,-0.027763957,-0.0143669965,0.007845481,-0.00795035,0.024853855,0.020528026,0.014209693,0.009824876,0.00863855,-0.02516846,0.013239659,-0.0016778974,0.021471843,-0.0021022875,-0.019544883,0.001977756,0.0049583176,0.0031575277,-0.004604386,-0.017591706,0.02388382,-0.004771521,0.0077209496,-0.003270589,0.030018633,0.010847344,-0.03371525,-0.016123544,-0.0053384663,0.0023431575,0.004620772,0.02672838,0.0070917383,-0.0182864…_
The procedure called **_GENERATE\_EMBEDDINGS_** does the conversion to vector.
This procedure is not a procedure in SQL Server. AzureSQL has this feature, but not on-prem.
Here, it connects to the Azure OpenAI service and performs the conversion to vector.
![](https://omercolakoglu.net/wp-content/uploads/2024/11/image-5.png?w=945)
Now let’s look at how we make a comparison between two vectors.
Here we use a formula called cosine distance.

**3.Vector Similarity Comparison Cosine Distance**
Cosine distance is a distance metric used to measure similarity between two vectors.  It is based on the angle between two vectors.
When vectors are facing the same direction, they are considered similar, as they look in different directions, the distance between them increases.
**Simply put:**
1.  Cosine distance calculates the cosine of the angle between two vectors and gives the degree of similarity.
2.  The larger the cosine of the angle (close to 1), the more similar the two vectors are.
3.  As the cosine distance value approaches 0, the vectors are similar to each other, and as they approach 1, they are different.

![](https://omercolakoglu.net/wp-content/uploads/2024/11/image-6.png?w=400)
It is used to measure content similarity, especially in large data sets such as text and documents.
Of course, since the concept we call vector here is a series with 768 elements, we are talking about a subject that includes all the elements of the vector.
As can be seen in the picture below
Which is a search phrase
_‘I am looking for a Lenovo or Samsonite notebook bag.’_
With the record in the database
_“Lenovo ThinkPad Essential Plus 15.6 Eco Backpack Lenovo 4X41A30364 15.6 Notebook Backpack OverviewThe perfect blend of professionalism and athleticism, the ThinkPad Essential Plus 15.6 Backpack (Eco) can take you from the office to the gym and back with ease. Spacious compartments keep your devices and essentials safe, organized, and accessible, while ballistic nylon and durable hardware protect against the elements and everyday wear and tear. Dedicated, separate laptop compartmentProtect your belongings with the hidden security pocket and luggage strap. Stay hydrated with two expandable side water bottle pockets. Laptop Size Range: 15 – 16 inches, Volume (L): 15, Bag Type: Backpack, Screen Size (inch): 15.6, Color: Black, Warranty Period (Months): 24, International Sales: None, Stock Code: HBCV00000VIMV8 Number of Reviews: 18Reviews Brand: Lenovo Seller: JetKlik Seller Rating: 9.6”_
You see the vectors of the sentence translated into vectors and the similarity between them.
![](https://omercolakoglu.net/wp-content/uploads/2024/11/image-7.png?w=945)
Being able to search for similarities from the database through vectors allows us to use the database like a chatbot.
In this case, we can perform a search operation like writing a prompt. There is already such a command in Azure SQL.
It calculates the cosine distance between two vectors and the similarity accordingly.
You can access the article on the subject from the link below.
![](https://omercolakoglu.net/wp-content/uploads/2024/11/image-8.png?w=945)
[https://github.com/Azure-Samples/azure-sql-db-vector-search/blob/main/Vector-Search/VectorSearch.ipynb](https://github.com/Azure-Samples/azure-sql-db-vector-search/blob/main/Vector-Search/VectorSearch.ipynb)
Here, we’ll try to perform a situation that already exists on Azure SQL on On Prem SQL Server.
First of all, let’s look at how to convert to vector.
We have a table like below.
![](https://omercolakoglu.net/wp-content/uploads/2024/11/image-9.png?w=945)
In this table, the **DESCRIPTION\_** field is a non-structured text field that contains all the properties of the product. Since we are going to search on this field, we must convert this field to vector.
Since there is no code that converts directly to vector on SQL Server for now, we will do this with an external plugin here. There are a variety of language models here. For example, we can use the Azure Open AI service.
I wrote a procedure like this.
```SQL
CREATE PROCEDURE [dbo].[GENERATE_EMBEDDINGS]
@INPUT_TEXT NVARCHAR(MAX) = N'I am looking for a Lenovo or Samsonite brand notebook bag',
@VECTORSTR NVARCHAR(MAX) OUTPUT
AS
set @input_text=replace(@input_text,'"','\"')
DECLARE @Object AS INT;
DECLARE @ResponseText AS NVARCHAR(MAX)
DECLARE @StatusText AS nVARCHAR(800);
DECLARE @URL AS NVARCHAR(MAX);
DECLARE @Body AS NVARCHAR(MAX);
DECLARE @ApiKey AS VARCHAR(800);
DECLARE @Status AS INT;
DECLARE @hr INT;
DECLARE @ErrorSource AS VARCHAR(max);
DECLARE @ErrorDescription AS VARCHAR(max);
DECLARE @Headers  nVARCHAR(MAX);
DECLARE @Payload  nVARCHAR(MAX);
DECLARE @ContentType  nVARCHAR(max);
--SET NOCOUNT on
SET @URL = 'https://omeropenaiservice.openai.azure.com/openai/deployments/text-embedding-ada-002/embeddings?api-version=2023-05-15';
SET @Headers = 'api-key: 584eXXXXXXXXXXXXXXXXXXXXXXX';

--Payload to send
SET @Payload = '{"input": "' + @input_text + '"}';


SET @ApiKey = 'api-key: 584eXXXXXXXXXXXXXXXXXXXXXX'
--SET @URL = 'https://api.openai.com/v1/embeddings';
SET @Body =  '{"input": "' + @input_text + '"}'-- '{"input": "' + @input_text + '"}';--'{"model": "text-embedding-ada-002", "input": "' + REPLACE(@input_text, '"', '\"') + '"}';

print @body
-- Create OLE Automation object
EXEC @hr = sp_OACreate 'MSXML2.ServerXMLHTTP', @Object OUT;
IF @hr <> 0
BEGIN
EXEC sp_OAGetErrorInfo @Object, @ErrorSource OUT, @ErrorDescription OUT;
PRINT 'Failed to create OLE object';
PRINT 'Error Source: ' + @ErrorSource;
PRINT 'Error Description: ' + @ErrorDescription;
RETURN;
END

-- Open connection
EXEC @hr = sp_OAMethod @Object, 'open', NULL, 'POST', @URL, 'false';
IF @hr <> 0
BEGIN
EXEC sp_OAGetErrorInfo @Object, @ErrorSource OUT, @ErrorDescription OUT;
PRINT 'Failed to open connection';
PRINT 'Error Source: ' + @ErrorSource;
PRINT 'Error Description: ' + @ErrorDescription;
EXEC sp_OADestroy @Object;
RETURN;
END

-- Set request headers
EXEC @hr = sp_OAMethod @Object, 'setRequestHeader', NULL, 'Content-Type', 'application/json';
EXEC @hr = sp_OAMethod @Object, 'setRequestHeader', NULL, 'api-key', '584XXXXXXXXXXXXXXXXXXXXX';
IF @hr <> 0
BEGIN
EXEC sp_OAGetErrorInfo @Object, @ErrorSource OUT, @ErrorDescription OUT;
PRINT 'Failed to set Content-Type header';
PRINT 'Error Source: ' + @ErrorSource;
PRINT 'Error Description: ' + @ErrorDescription;
EXEC sp_OADestroy @Object;
RETURN;
END

EXEC @hr = sp_OAMethod @Object, 'setRequestHeader', NULL, 'Authorization', @ApiKey;
IF @hr <> 0
BEGIN
EXEC sp_OAGetErrorInfo @Object, @ErrorSource OUT, @ErrorDescription OUT;
PRINT 'Failed to set Authorization header';
PRINT 'Error Source: ' + @ErrorSource;
PRINT 'Error Description: ' + @ErrorDescription;
EXEC sp_OADestroy @Object;
RETURN;
END

-- Send request
EXEC @hr = sp_OAMethod @Object, 'send', NULL, @Body;
IF @hr <> 0
BEGIN
EXEC sp_OAGetErrorInfo @Object, @ErrorSource OUT, @ErrorDescription OUT;
PRINT 'Failed to send request';
PRINT 'Error Source: ' + @ErrorSource;
PRINT 'Error Description: ' + @ErrorDescription;
EXEC sp_OADestroy @Object;
RETURN;
END

-- Get HTTP status
EXEC @hr = sp_OAMethod @Object, 'status', @Status OUT;
IF @hr <> 0
BEGIN
EXEC sp_OAGetErrorInfo @Object, @ErrorSource OUT, @ErrorDescription OUT;
PRINT 'Failed to get HTTP status';
PRINT 'Error Source: ' + @ErrorSource;
PRINT 'Error Description: ' + @ErrorDescription;
EXEC sp_OADestroy @Object;
RETURN;
END

-- Get status text
EXEC @hr = sp_OAMethod @Object, 'statusText', @StatusText OUT;
IF @hr <> 0
BEGIN
EXEC sp_OAGetErrorInfo @Object, @ErrorSource OUT, @ErrorDescription OUT;
PRINT 'Failed to get HTTP status text';
PRINT 'Error Source: ' + @ErrorSource;
PRINT 'Error Description: ' + @ErrorDescription;
EXEC sp_OADestroy @Object;
RETURN;
END

-- Print status and status text
PRINT 'HTTP Status: ' + CAST(@Status AS NVARCHAR);
PRINT 'HTTP Status Text: ' + @StatusText;

IF @Status <> 200
BEGIN
PRINT 'HTTP request failed with status code ' + CAST(@Status AS NVARCHAR);
EXEC sp_OADestroy @Object;
RETURN;
END

-- Get response text
DECLARE @json TABLE (Result NVARCHAR(MAX))
INSERT  @json(Result)
EXEC    dbo.sp_OAGetProperty @Object, 'responseText'
SELECT  @ResponseText = Result FROM @json

-- Print response text
--SELECT @ResponseText;

-- Destroy OLE Automation object
DECLARE @t AS TABLE (EmbeddingValue nVARCHAR(MAX))

-- Splitting embedded array

SET @vectorstr = (
SELECT EmbeddingValue + ','
FROM (
SELECT value AS EmbeddingValue
FROM OPENJSON(@ResponseText, '$.data[0].embedding')
) t
FOR XML PATH('')
)

SET @vectorstr = SUBSTRING(@vectorstr, 1, LEN(@vectorstr) - 1)

```


Here is how it’s used.

The vector uses the “text-embedding-ada-002” model and creates a vector with 1536 elements.

![](https://omercolakoglu.net/wp-content/uploads/2024/11/image-10.png?w=945)

Alternatively, we can write a code ourselves in Python without using Azure and we can do vector transformation through another model.

```python
from flask import Flask, request, jsonify
import openai

app = Flask(__name__)

# Azure OpenAI API connection details
openai.api_type = "azure"
openai.api_key = "8nnCxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
openai.api_base = "https://omeropenaiservice.openai.azure.com/"
openai.api_version = "2024-08-01-preview"

# Embedding model and maximum token limit
EMBEDDING_MODEL = "text-embedding-ada-002"
MAX_TOKENS = 8000
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# Function to generate embeddings using Azure OpenAI API
def get_embedding(text):
    embeddings = []
    tokens = text.split()  # Split the text into tokens using whitespace

    # Split the text into chunks and process each chunk
    for i in range(0, len(tokens), MAX_TOKENS):
        chunk = ' '.join(tokens[i:i + MAX_TOKENS])
        response = openai.Embedding.create(
            engine=EMBEDDING_MODEL,  # Use 'engine' instead of 'model' in Azure OpenAI
            input=chunk
        )
        embedding = response['data'][0]['embedding']
        embeddings.append(embedding)
        print(f"Chunk {i // MAX_TOKENS + 1} processed")  # Log progress
    return embeddings

# API endpoint for vectorization
@app.route('/vectorize', methods=['POST'])
def vectorize():
    data = request.json
    text = data.get('text', '')

    if not text or text.strip() == "":
        return jsonify({"error": "Invalid or empty input"}), 400

    try:
        vector = get_embedding(text)
        return jsonify({"vector": vector})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)


```


![](https://omercolakoglu.net/wp-content/uploads/2024/11/ccb89cb8-9535-4c7c-a884-446277bfccc9.png?w=943)

Alternatively, we can write a code ourselves in Python without using Azure and we can do vector transformation through another model.

This code creates a vector with 1536 elements, which takes a string expression into it and consequently converts the vector according to the “all-mpet-base-v2” model.

```python
from flask import Flask, request, jsonify
from sentence_transformers import SentenceTransformer

# Initialize Flask app and model
app = Flask(__name__)
model = SentenceTransformer('all-mpnet-base-v2')

# Define an endpoint that returns a vector
@app.route('/get_vector', methods=['POST'])
def get_vector():
    # Retrieve text from JSON request
    data = request.get_json()
    if 'text' not in data:
        return jsonify({"error": "Request must contain 'text' field"}), 400

    try:
        # Convert the text to a vector
        embedding = model.encode(data['text'])

        # Convert the embedding vector to a list and return as JSON
        return jsonify({"vector": embedding.tolist()})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Run the Flask app
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
```


![](https://omercolakoglu.net/wp-content/uploads/2024/11/a787bfa0-c70b-4d08-b189-3ed835852039.png?w=622)

Now let’s write the TSQL code that will call this API from SQL.

```SQL
create PROCEDURE [dbo].[GENERATE_EMBEDDINGS_LOCAL]
    @str NVARCHAR(MAX),
    @vector NVARCHAR(MAX) OUTPUT
AS
BEGIN
DECLARE @Object INT;
DECLARE @ResponseText NVARCHAR(MAX);
DECLARE @StatusCode INT;
DECLARE @URL NVARCHAR(MAX) = 'http://127.0.0.1:5000/get_vector';
DECLARE @HttpRequest NVARCHAR(MAX);
DECLARE @StatusText AS nVARCHAR(800);
DECLARE @Body AS NVARCHAR(MAX);
DECLARE @ApiKey AS VARCHAR(800);
DECLARE @Status AS INT;
DECLARE @hr INT;
DECLARE @ErrorSource AS VARCHAR(max);
DECLARE @ErrorDescription AS VARCHAR(max);
DECLARE @Headers  nVARCHAR(MAX);
DECLARE @Payload  nVARCHAR(MAX);
DECLARE @ContentType  nVARCHAR(max);
 
SET @Body = '{"text": "' + @str + '"}'
 
print @body 
-- Create OLE Automation object
EXEC @hr = sp_OACreate 'MSXML2.ServerXMLHTTP', @Object OUT;
IF @hr <> 0
BEGIN
    EXEC sp_OAGetErrorInfo @Object, @ErrorSource OUT, @ErrorDescription OUT;
    PRINT 'Failed to create OLE object';
    PRINT 'Error Source: ' + @ErrorSource;
    PRINT 'Error Description: ' + @ErrorDescription;
    RETURN;
END

-- Open connection
EXEC @hr = sp_OAMethod @Object, 'open', NULL, 'POST', @URL, 'false';
IF @hr <> 0
BEGIN
    EXEC sp_OAGetErrorInfo @Object, @ErrorSource OUT, @ErrorDescription OUT;
    PRINT 'Failed to open connection';
    PRINT 'Error Source: ' + @ErrorSource;
    PRINT 'Error Description: ' + @ErrorDescription;
    EXEC sp_OADestroy @Object;
    RETURN;
END

-- Set request headers
EXEC @hr = sp_OAMethod @Object, 'setRequestHeader', NULL, 'Content-Type', 'application/json';
 
IF @hr <> 0
BEGIN
    EXEC sp_OAGetErrorInfo @Object, @ErrorSource OUT, @ErrorDescription OUT;
    PRINT 'Failed to set Content-Type header';
    PRINT 'Error Source: ' + @ErrorSource;
    PRINT 'Error Description: ' + @ErrorDescription;
    EXEC sp_OADestroy @Object;
    RETURN;
END
 

-- Send request
EXEC @hr = sp_OAMethod @Object, 'send', NULL, @Body;
IF @hr <> 0
BEGIN
    EXEC sp_OAGetErrorInfo @Object, @ErrorSource OUT, @ErrorDescription OUT;
    PRINT 'Failed to send request';
    PRINT 'Error Source: ' + @ErrorSource;
    PRINT 'Error Description: ' + @ErrorDescription;
    EXEC sp_OADestroy @Object;
    RETURN;
END

-- Get HTTP status
EXEC @hr = sp_OAMethod @Object, 'status', @Status OUT;
IF @hr <> 0
BEGIN
    EXEC sp_OAGetErrorInfo @Object, @ErrorSource OUT, @ErrorDescription OUT;
    PRINT 'Failed to get HTTP status';
    PRINT 'Error Source: ' + @ErrorSource;
    PRINT 'Error Description: ' + @ErrorDescription;
    EXEC sp_OADestroy @Object;
    RETURN;
END

-- Get status text
EXEC @hr = sp_OAMethod @Object, 'statusText', @StatusText OUT;
IF @hr <> 0
BEGIN
    EXEC sp_OAGetErrorInfo @Object, @ErrorSource OUT, @ErrorDescription OUT;
    PRINT 'Failed to get HTTP status text';
    PRINT 'Error Source: ' + @ErrorSource;
    PRINT 'Error Description: ' + @ErrorDescription;
    EXEC sp_OADestroy @Object;
    RETURN;
END

-- Print status and status text
PRINT 'HTTP Status: ' + CAST(@Status AS NVARCHAR);
PRINT 'HTTP Status Text: ' + @StatusText;

IF @Status <> 200
BEGIN
    PRINT 'HTTP request failed with status code ' + CAST(@Status AS NVARCHAR);
    EXEC sp_OADestroy @Object;
    RETURN;
END

-- Get response text
DECLARE @json TABLE (Result NVARCHAR(MAX))
INSERT  @json(Result)
EXEC    dbo.sp_OAGetProperty @Object, 'responseText'
SELECT  @ResponseText = Result FROM @json
 
 
-- Destroy OLE Automation object
DECLARE @t AS TABLE (EmbeddingValue nVARCHAR(MAX))
 
 
 
SET @vector = (
    SELECT EmbeddingValue + ','
    FROM (
        SELECT value AS EmbeddingValue
        FROM OPENJSON(@ResponseText, '$.vector')
    ) t
    FOR XML PATH('')
)

 SET @vector = SUBSTRING(@vector , 1, LEN(@vector ) - 1)
End
```


Here is, how it’s used.

![](https://omercolakoglu.net/wp-content/uploads/2024/11/image-12.png?w=945)

Now let’s convert this to vector for the field we added to the table. I’ll be using the local Azure Open AI service here. The following query converts the field VECTOR\_1536 (I used this name because it is a field with 1536 elements) to vector and updates it for all rows in the table.

![](https://omercolakoglu.net/wp-content/uploads/2024/11/image-13.png?w=945)

After a long process, our vector column is now ready and now, we will do a similarity search on this column.

**Cosine Distance Calculation Method**

```python
import numpy as np
from sklearn.metrics.pairwise import cosine_distances

# Example vectors
A = np.array([1, 2, 3])
B = np.array([4, 5, 6])

# Manual calculation of cosine similarity
cosine_similarity = np.dot(A, B) / (np.linalg.norm(A) * np.linalg.norm(B))
cosine_distance = 1 - cosine_similarity
print("Cosine Distance (manual):", cosine_distance)

# Calculating cosine distance with sklearn
cosine_distance_sklearn = cosine_distances([A], [B])[0][0]
print("Cosine Distance (sklearn):", cosine_distance_sklearn)

```


![](https://omercolakoglu.net/wp-content/uploads/2024/11/799b6c59-98a8-431e-b564-c563c7567203.png?w=595)

**Cosine Distance is calculated as follows.**

As an example, we have two vectors with 3 elements.

_Vector1=\[0.5,0.3,-0.8\]_

Vector2=\[-0.2,0.4,0.9\]

Here, the cosine distance is calculated as follows.

The sum of each element multiplied by each other is @dotproduct

_@dotproduct=(0.5x(-0.2))+(0.3×0.4)+(-0.8×0.9) =-0.7_

The sum of the squares of each element is @magnitude1, @magnitude2

_@magnitude1=(0.5×0.5)+(0.3×0.3)+(-0.8x-0.8)=0.98_

_@magnitude2=(-0.2x-0.2)+( 0.4×0.4)+( 0.9×0.9)=1.01_

To calculate similarity,

_@similarity=@dotproduct / (SQRT(@magnitude1) \* SQRT(@magnitude2));_

```SQL
DECLARE @Vector1 AS NVARCHAR(MAX) = '[0.5,0.3,-0.8]'
DECLARE @Vector2 AS NVARCHAR(MAX) = '[-0.2,0.4,0.9]'
DECLARE @dotproduct AS FLOAT
DECLARE @magnitude1 AS FLOAT
DECLARE @magnitude2 AS FLOAT

SET @dotproduct = (0.5 * (-0.2)) + (0.3 * 0.4) + (-0.8 * 0.9)
SET @magnitude1 = (0.5 * 0.5) + (0.3 * 0.3) + (-0.8 * -0.8)
SET @magnitude2 = (-0.2 * -0.2) + (0.4 * 0.4) + (0.9 * 0.9)

DECLARE @Similarity AS FLOAT
SET @Similarity = @dotproduct / (SQRT(@magnitude1) * SQRT(@magnitude2))

SELECT @dotproduct DotProduct
    ,@magnitude1 Magnitude1
    ,@magnitude2 Magnitude2
    ,@Similarity Similarity

```


![](https://omercolakoglu.net/wp-content/uploads/2024/11/image-15.png?w=945)

**Cosine Distance Calculation Example with TSQL**

![](https://omercolakoglu.net/wp-content/uploads/2024/11/image-16.png?w=945)

```SQL
CREATE FUNCTION [dbo].[CosineSimilarity] (
@Vector1 NVARCHAR(MAX), @Vector2 NVARCHAR(MAX)
)
RETURNS FLOAT
AS
BEGIN
SET @Vector1 = REPLACE(@Vector1, '[', '')
SET @Vector1 = REPLACE(@Vector1, ']', '')

SET @Vector2 = REPLACE(@Vector2, '[', '')
SET @Vector2 = REPLACE(@Vector2, ']', '')

DECLARE @dot_product FLOAT = 0, @magnitude1 FLOAT = 0, @magnitude2 FLOAT = 0;
DECLARE @val1 FLOAT, @val2 FLOAT;
DECLARE @i INT = 0;
DECLARE @v1 NVARCHAR(MAX), @v2 NVARCHAR(MAX);
DECLARE @len INT;

-- Split vectors and insert into tables
DECLARE @tvector1 TABLE (ID INT, Value FLOAT);
DECLARE @tvector2 TABLE (ID INT, Value FLOAT);

INSERT INTO @tvector1
SELECT ordinal, CONVERT(FLOAT, value) FROM STRING_SPLIT(@Vector1, ',', 1) ORDER BY 2;

INSERT INTO @tvector2
SELECT ordinal, CONVERT(FLOAT, value) FROM STRING_SPLIT(@Vector2, ',', 1) ORDER BY 2;

SET @len = (SELECT COUNT(*) FROM @tvector1);

-- Return NULL if vectors are of different lengths
IF @len <> (SELECT COUNT(*) FROM @tvector2)
RETURN NULL;

-- Calculate cosine similarity
WHILE @i < @len
BEGIN
SET @i = @i + 1;

SELECT @val1 = Value FROM @tvector1 WHERE ID = @i;
SELECT @val2 = Value FROM @tvector2 WHERE ID = @i;

SET @dot_product = @dot_product + (@val1 * @val2);
SET @magnitude1 = @magnitude1 + (@val1 * @val1);
SET @magnitude2 = @magnitude2 + (@val2 * @val2);
END

-- Return 0 if any magnitude is zero to avoid division by zero
IF @magnitude1 = 0 OR @magnitude2 = 0
RETURN 0;

RETURN @dot_product / (SQRT(@magnitude1) * SQRT(@magnitude2));
END
```


Now let’s compare a vector in db with a string expression.

```SQL
-- Creating a search sentence and converting it to a vector
DECLARE @VECTOR1 AS VARCHAR(MAX) = '1,2,3,4,5,6,7,8';
DECLARE @VECTOR2 AS VARCHAR(MAX) = '2,0,3,4,5,6,7,8';

SELECT dbo.CosineSimilarity(@VECTOR1, @VECTOR2);

-- Creating a search sentence and converting it to a vector
DECLARE @query AS NVARCHAR(MAX) = 'I am looking for a notebook bag';
DECLARE @searchVector AS NVARCHAR(MAX);
EXEC GENERATE_EMBEDDINGS @query, @searchVector OUTPUT;

-- Converting the DESCRIPTION2 field from a selected row in the database to a vector
DECLARE @dbText AS NVARCHAR(MAX);
DECLARE @dbVector AS NVARCHAR(MAX);
SELECT @dbText = DESCRIPTION_ FROM WEBITEMS WHERE ID = 80472;
EXEC GENERATE_EMBEDDINGS @dbText, @dbVector OUTPUT;

-- Displaying the vectors and sentences
SELECT @query AS Query, @searchVector AS SearchVector;
SELECT @dbText AS DBText, @dbVector AS DBVector;

-- Calculating the similarity and cosine distance values between the two vectors
SELECT dbo.CosineSimilarity(@searchVector, @dbVector) AS Similarity, 
       1 - dbo.CosineSimilarity(@searchVector, @dbVector) AS CosineDistance;
```


![](https://omercolakoglu.net/wp-content/uploads/2024/11/image-17.png?w=945)

As can be seen, the similarity of these two text expressions with each other was 0.63. Here we have calculated the similarity with only one record at the moment. However, what should happen is that this similarity is calculated among all the records in the database and a certain number of records come according to the one with the most similarity rate.

Since there are more than **75.000** records in the database, this function needs to run more than **75.000** times. This is a serious performance issue. Let’s run it for **100** rows of records.

![](https://omercolakoglu.net/wp-content/uploads/2024/11/image-18.png?w=945)

As you can see, even for **100** rows of data, it took **2** minutes. This means approximately **2×1000 = 2.000** minutes for 100 thousand lines, which is about **33 hours.**

It’s not abnormal for this amount of time to be.

Because that’s exactly what we’re doing in the background.

**1**.@dotProduct, there is a multiplication of elements as many as the number of elements of the vectors (our number is 1536) with each other, and then there is the addition of them.

**1536 Multiplication+1536 addition=3072 operations**

2.There is a process of calculating the sum of the elements by taking the squares of the elements for each vector.

Squaring operation for both vectors **1536 +1536 =3072 operations**.

3\. Finally, the

**@dotproduct / (SQRT(@magnitude1) \* SQRT(@magnitude2))**

There is a transaction, but it doesn’t matter because it happens 1 time.

In this case, for every vector with **1536** elements, **3072 + 3072 = 6144**  operations occur in each line.

In a table of 75.000 rows, this number means 75,000×6144  =460.800.000 (Approximately 460 million) mathematical operations. Therefore, it is possible that it will take so long.

![](https://omercolakoglu.net/wp-content/uploads/2024/11/image-19.png?w=945)

In short, it is not very healthy for us to calculate in this way.

**What to do to speed up this work?**

Yes, now let’s talk about how to speed up this work.

I’ve said many times that SQL Server likes to work with data in a vertical.

By vertical, I mean the data in the rows and the correct indexes.

But where is the vector data we have? 1536  horizontal data, which is distinguished by a comma next to each other, and sometimes 768 horizontal data according to the language model used.

SQL Server is not good at horizontal data. So how about we convert this horizontal data to vertical?

In other words, if we add each element of the vector to the system as a line.

We will create a table for this.

```SQL
CREATE TABLE VECTORDETAILS(
id int IDENTITY(1,1) NOT NULL,
vector_id [int] NOT NULL,
value_ float NULL,
key_ int NOT NULL
) ON [PRIMARY]
```


Here we will keep the ID value for a product as Vector\_id here. We will key\_ the sequence number of the vector element and keep its value as value\_.

As an example, let’s look at the product with ID **80472**.

![](https://omercolakoglu.net/wp-content/uploads/2024/11/image-20.png?w=945)

We can read the VECTOR\_1536 field line by line with splitting with the comma.

![](https://omercolakoglu.net/wp-content/uploads/2024/11/image-21.png?w=945)

Now let’s write a stored procedure for each product that will update it in the table.

```SQL
CREATE TABLE [dbo].[VECTORDETAILS](
	[id] [int] IDENTITY(1,1) NOT NULL,
	[vector_id] [int] NOT NULL,
	[value_] [float] NULL,
	[key_] [int] NULL
) ON [PRIMARY]
GO

CREATE PROC [dbo].[fillVectorDetailsContentByVectorId_WEBITEMS]
@vectorId as int
 
CREATE PROCEDURE [dbo].[FILL_VECTORDETAILS_BY_ID]
    @VECTOR_ID INT
AS
BEGIN
    DELETE FROM VECTORDETAILS WHERE VECTOR_ID = @VECTOR_ID;

    INSERT INTO VECTORDETAILS (VECTOR_ID, KEY_, VALUE_)
    SELECT 
        E.ID,
        D.ORDINAL,
        TRY_CONVERT(FLOAT, D.VALUE)
    FROM WEBITEMS E
    CROSS APPLY STRING_SPLIT(REPLACE(REPLACE(CONVERT(NVARCHAR(MAX), E.VECTOR_1536), ']', ''), '[', ''), ',',1) D
    WHERE E.VECTOR_1536 IS NOT NULL
    AND E.ID = @VECTOR_ID;
END;


```


![](https://omercolakoglu.net/wp-content/uploads/2024/11/image-22.png?w=945)

Now let’s call this procedure for all products.

```SQL
DECLARE @VECTORID AS INT;
DECLARE CRS CURSOR
FOR
SELECT ID
FROM WEBITEMS;
OPEN CRS;
FETCH NEXT
FROM CRS
INTO @VECTORID;
WHILE @@FETCH_STATUS = 0
BEGIN
    EXEC FILL_VECTORDETAILS_BY_ID @VECTORID;
    FETCH NEXT
    FROM CRS
    INTO @VECTORID;
END;
CLOSE CRS;
DEALLOCATE CRS;


```


![](https://omercolakoglu.net/wp-content/uploads/2024/11/image-24.png?w=945)

**Cosine Simularity Fast Calculation**

Yes, now that we have come this far, the next step is to quickly calculate similarity. There’s a TSQL code I wrote for this.

— Declare variables

DECLARE @input\_text NVARCHAR(MAX)   =’I am looking for a Lenovo or Samsonite brand notebook bag’;

DECLARE @vectorstr NVARCHAR(MAX);

DECLARE @vector NVARCHAR(MAX);

— Remove special characters from the input text

SET @input\_text = dbo.RemoveSpecialChars(@input\_text);

DECLARE @outputVector NVARCHAR(MAX);

EXEC GENERATE\_EMBEDDINGS  @input\_text, @vectorstr OUTPUT;

— Create a temporary table to store the vector values

CREATE TABLE #t (

       vector\_id INT,

    key\_ INT,

    value\_ FLOAT

);

— Insert vector values into the temporary table

INSERT INTO #t (vector\_id, key\_, value\_)

SELECT

       -1 AS vector\_id,  — Use -1 as the vector ID for the input text

       d.ordinal AS key\_,  — The position of the value in the vector

       CONVERT(FLOAT, d.value) AS value\_   — The value of the vector

FROM

STRING\_SPLIT(@vectorstr, ‘,’, 1) AS d

— Calculate the cosine similarity between the input vector and stored vectors

SELECT TOP 100 

   vector\_id,

   SUM(dot\_product) / SUM(SQRT(magnitude1) \* SQRT(magnitude2)) AS Similarity,

   @input\_text AS SearchedQuery,  — Include the input query for reference

   (

       SELECT TOP 1  DESCRIPTION\_ 

          FROM  WEBITEMS

          WHERE ID = TT.vector\_id

   ) AS SimilarTitle  — Fetch the most similar title from the walmart\_product\_details table

       into #t1

    FROM

    (

        SELECT

            T.vector\_id,

            SUM(VD.value\_ \* T.value\_) AS dot\_product,  — Dot product of input and stored vectors

            SUM(VD.value\_\*VD.value\_) AS magnitude1,  — Magnitude of the input vector

            SUM(T.value\_\*T.value\_) AS magnitude2  — Magnitude of the stored vector

        FROM

            #t VD  — Input vector data

        CROSS APPLY

        (

            — Retrieve stored vectors where the key matches the input vector key

            SELECT    \*

            FROM VECTORDETAILS vd2

            WHERE key\_ = VD.key\_

        ) T

        GROUP BY T.vector\_id  — Group by vector ID to calculate the similarity for each stored vector

    ) TT

GROUP BY vector\_id  — Group the final similarity results by vector ID

ORDER BY 2 DESC;  — Order by similarity in descending order (most similar first)

select DISTINCT   vector\_id,ROUND(similarity,5) Similarity,similarTitle ProductName from #t1

WHERE similarTitle IS NOT NULL

ORDER BY 2 DESC

DROP TABLE #t,#t1 ;

![](https://omercolakoglu.net/wp-content/uploads/2024/11/image-25.png?w=945)

The query seems to be working fine, but the duration is 11 seconds. Actually this is very great time. Because, remember! The first calculation time for the cosinus distance was about 33 hours with table scan.

But I think it can be better.

Let’s work!

We don’t have any nonclustered index for now and we have just primary key for ID column and we have a clustered index for this auto Increment integer field. But our query Works on VECTOR\_ID and KEY\_ columns.

Let’s try to make these columns primary key.

```SQL
ALTER TABLE VECTORDETAILS ADD PRIMARY KEY (KEY_,VECTOR_ID)

```


And try again.

Wee see, the result is same before.

![](https://omercolakoglu.net/wp-content/uploads/2024/11/image-26.png?w=945)

Let’s change the order of primary key columns.
Let’s change the order of primary key columns.

![](https://omercolakoglu.net/wp-content/uploads/2024/11/image-27.png?w=945)

We can try the columnstore index.

![](https://omercolakoglu.net/wp-content/uploads/2024/11/image-28.png?w=945)

With Clustered columnstore index, the duration is 5 seconds.

It is 2 times faster than normal clustered index. It is normal. Because we are calculating summary for every vector and they have 1536 elements. If you are working with aggregation and summary, Columnstore indexes are faster.

![](https://omercolakoglu.net/wp-content/uploads/2024/11/image-29.png?w=945)

But we also querying data with the KEY\_ and VECTOR\_ID fields.

We are joining our search vector and the all vectors in our table. (80.000 rows)

We are joining them with the key\_ column.

If we use just clustered columnstore index it will be slow. Because CC Indexes are faster for batch reading and aggregating. For row based comprasion, Nonclustered indexes are better.

So we need a non clustered index for the key\_ column and also we need included column to decrease to read.

![](https://omercolakoglu.net/wp-content/uploads/2024/11/image-30.png?w=945)

```SQL
CREATE INDEX IX1 ON VECTORDETAILS(KEY_)
INCLUDE (VECTOR_ID,VALUE_)
```


With Clustered Columnstore Index and Nonclustered index with Key\_ column

The duration is 4 seconds. 20% faster than before. Not bad but we expect more.

![](https://omercolakoglu.net/wp-content/uploads/2024/11/image-31.png?w=945)

Let’s turn back to Cosine similarity formula.

**1.DotProduct:** In other words, the elements of both vectors in the same order are multiplied by each other.

**2.Magnitude1, Magnitude2:** The process of summarizing all the elements of both vectors by squaring them and then taking the square root again.

There is no escaping operation for number one.  Because it is related to the other vectors in the table.

But for number two, we can decrease reading  by calculating it at once and there is no need to calculate it again.

We should add another field to our table and update it.

```SQL
Alter Table VECTORDETAILS  add valsqrt float
Update VECTORDETAILS set valsqrt=value*value_
Now let's add a separate table to calculate the magnitude values.

CREATE TABLE VECTORSUMMARY (
ID INT IDENTITY(1,1),
VECTOR_ID INT,
MAGNITUDE FLOAT,
MAGNITUDESQRT FLOAT
```

```SQL
Alter Table VECTORDETAILS  add valsqrt float
Update VECTORDETAILS set valsqrt=value\*value\_
```
Now let’s add a separate table to calculate the magnitude values.

```SQL
CREATE TABLE VECTORSUMMARY (
ID INT IDENTITY(1,1),
VECTOR\_ID INT,
MAGNITUDE FLOAT,
MAGNITUDESQRT FLOAT)
```
Now let’s group it from the VECTORDETAILS table and insert it here.
```SQL
INSERT INTO VECTORSUMMARY
(VECTOR_ID, MAGNITUDE, MAGNITUDESQRT)
select  VECTOR_ID,SUM(VALSQRT) ,SQRT( SUM(VALSQRT) )
FROM VECTORDETAILS
WHERE VECTOR_ID=@vectorId
GROUP BY VECTOR_ID
)
```
Finally, let's create an index.
```SQL
CREATE NONCLUSTERED INDEX IX1 ON dbo.VECTORSUMMARY
(
VECTOR_ID ASC
)
INCLUDE(ID,MAGNITUDE, MAGNITUDESQRT)
```


Now let’s modify and run our calculation query accordingly.

```SQL
DECLARE @input_text nVARCHAR(MAX) = N'I am looking for a Lenovo or Samsonite brand notebook bag';
DECLARE @vectorstr nVARCHAR(MAX);
DECLARE @outputVector NVARCHAR(MAX);
EXEC  GENERATE_EMBEDDINGS @input_text,  @vectorstr OUTPUT;
CREATE TABLE #t (
vector_id INT
,key_ INT
,value_ FLOAT
,valsqrt FLOAT
,magnitude FLOAT
);

-- Insert vector values into the temporary table
INSERT INTO #t (
vector_id
,key_
,value_
,valsqrt
)
SELECT - 1 AS vector_id
,-- Use -1 as the vector ID for the input text
d.ordinal AS key_
,-- The position of the value in the vector
CONVERT(FLOAT, d.value) AS value_
,-- The value of the vector
CONVERT(FLOAT, d.value) * CONVERT(FLOAT, d.value) AS valsqrt -- Squared value
FROM STRING_SPLIT(@vectorstr, ',', 1) AS d


CREATE INDEX IX1 ON #T (KEY_) INCLUDE (
[vector_id]
,[value_]
,[valsqrt]
)


DECLARE @magnitudesqrt AS FLOAT

SELECT @magnitudesqrt = sqrt(sum(valsqrt))
FROM #T

SELECT  top 100 T.vector_id
,dotProduct / (sqrt(@magnitudesqrt) * sqrt(vs.magnitudesqrt) ) CosineSimularity
,1 - (dotProduct / (@magnitudesqrt * vs.magnitudesqrt)) CosineDistance
,(
SELECT TOP 1 DESCRIPTION_
FROM WEBITEMS
WHERE id  = t.vector_id
) AS description
FROM (
SELECT v2.vector_id
,sum(v1.value_* v2.value_) dotproduct
FROM #t v1 WITH (NOLOCK)
INNER JOIN VECTORDETAILS  v2 WITH (NOLOCK) ON v1.key_ = v2.key_
GROUP BY v2.vector_id
,v1.magnitude
,V2.magnitude
) t
LEFT JOIN VECTORSUMMARY VS ON VS.vector_id = T.vector_id
ORDER BY 2 desc
DROP TABLE #t
```

Yes, as you can see now, the search process has decreased to 3 seconds.

![](https://omercolakoglu.net/wp-content/uploads/2024/11/image-33.png?w=945)

And last thing we can try is using Ordered Clustered Columnstore Index.
It is a new feature coming with SQL Server 2022 and it can increase the performance by reducing logical read count.
We should drop current clustered columnstore index. And create ordered version.
```SQL
DROP INDEX CCIX1 ON VECTORDETAILS
CREATE CLUSTERED COLUMNSTORE INDEX [CCIX1] ON [dbo].[VECTORDETAILS] 
ORDER (VECTOR_ID)WITH (COMPRESSION_DELAY = 0, DATA_COMPRESSION = COLUMNSTORE,MAXDOP=1) ON [PRIMARY]
GO
```


![](https://omercolakoglu.net/wp-content/uploads/2024/11/image-34.png?w=945)

Now, let’s try it with ordered clustered columnstore Index.

Yes! At the end, we did it! It is less than one second.

![](https://omercolakoglu.net/wp-content/uploads/2024/11/image-35.png?w=945)

![](https://omercolakoglu.net/wp-content/uploads/2024/11/image-36.png?w=945)

**The vector search process includes a universal search.**

In traditional text-based searches, you make a text-based, word-based comparison as you search. However, in vector search, you search as a semantic integrity. In text-based searches, for example, you cannot perform an English search within a Turkish data set. Or you need to translate the English text before the call.

But vector-based search is a bit like body language universal.

In other words, saying _“I’m looking for a laptop bag”_ and _“Bir notebook çantası arıyorum”_ are very close to each other.

This is how we can try.

![](https://omercolakoglu.net/wp-content/uploads/2024/11/image-37.png?w=945)

**Summary and Conclusion**

This article walks you through how to perform a vector search operation on On Prem SQL Server 2022.

Currently, since there is no vector search feature on SQL Server 2022, I searched with the algorithm written in **TSQL**.

In the vector conversion process, the ” “text-embedding-ada-002” model was used and vectors of **1536** elements were created.

In a table of **75.959** rows, vectors are converted to rows and stored in a table, and the number of rows in this table is **116.673.024 (about 116 million)**

![](https://omercolakoglu.net/wp-content/uploads/2024/11/image-38.png?w=828)

The Ordered Clustered Columnstore Index, which comes with SQL Server 2022, was used to perform performance search on this table.

The search performance results are as follows.

\-Search with cosine distance function on 75 thousand lines: 33 hours

\-Search via primary key by rowing vector elements on 75 thousand lines: 11 sec

\-Search on the Clustered Columnstore index by rowing vector elements on 75 thousand lines: 3 sec.

\-Search on the Clustered Columnstore index by rowing vector elements on 75 thousand lines: 380 ms.

**My Hardware**

Device features

Processor:13th Gen Intel(R) Core(TM) i7-13700H 2.40 GHz

Installed RAM:32.0GB

OS: Windows 11 64-bit operating system, x64-based processor

HDD: KINGSTON SNV2S2000G 1.81 TB

**Overall Rating**

Although vector search is not fully sufficient for search on its own, it brings a very different perspective with its quality as a new search approach and a language-independent semantic integrity search.

When combined with attribute extraction or text search, it will be able to produce very successful results.

In order to further increase system performance, partitioning can be tried on the Clustered Columnstore Index.

I hope you enjoyed it. Hope to see you in another article…

**Here is the ChatGPT Review**

![](https://omercolakoglu.net/wp-content/uploads/2024/11/image-39.png?w=945)

![](https://omercolakoglu.net/wp-content/uploads/2024/11/image-40.png?w=945)

![](https://omercolakoglu.net/wp-content/uploads/2024/11/image-41.png?w=850)

![](https://omercolakoglu.net/wp-content/uploads/2024/11/image-42.png?w=730)

![](https://omercolakoglu.net/wp-content/uploads/2024/11/image-43.png?w=826)

![](https://omercolakoglu.net/wp-content/uploads/2024/11/image-44.png?w=945)

![](https://omercolakoglu.net/wp-content/uploads/2024/11/92852589-ca1e-4c15-a481-4b43f6b75e44.png?w=620)
