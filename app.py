import json
import numpy as np
import pandas as pd
from scipy.stats import norm

# Constants are defined here
TRAIT_QUESTION_COUNT = 26
NEGATIVE_EXCEPTIONAL_QUESTION_COUNT = 4
POSITIVE_EXCEPTIONAL_QUESTION_COUNT = 4
APPRAISER_IMPRESSION_QUESTION_COUNT = 5
TRAIT_QUESTIONS = ["T" + ("00" + str(i))[-2:] for i in range(0, TRAIT_QUESTION_COUNT)]
NEGATIVE_EXCEPTIONAL_QUESTIONS = ["E00", "E01", "E02", "E03"]
POSITIVE_EXCEPTIONAL_QUESTIONS = ["E04", "E05", "E06", "E07"]
APPRAISER_IMPRESSION_QUESTIONS = ["A00", "A01", "A02", "A03", "A04"]
# Ensure that Appraisers overall score is coming in from A00
APPRAISER_IMPRESSION_OVERALL_QUESTION = "A00"
APPRAISER_IMPRESSION_WEIGHT = 0.3
OQ_QUESTION_WEIGHT = 0.7
TRAIT_WEIGHTS = np.array(
    [
        9.3,
        7.0,
        8.2,
        8.2,
        6.8,
        8.2,
        7.3,
        7.5,
        7.0,
        7.5,
        7.3,
        8.7,
        7.3,
        6.3,
        9.0,
        8.8,
        8.3,
        7.2,
        6.5,
        7.8,
        7.8,
        7.8,
        7.3,
        7.2,
        6.3,
        6.8,
    ]
)


def computeTraitBased(data):
    """Compute 'traitBased' column using values from T** columns
    :param data:
    :return:
    """
    traitScores = data[TRAIT_QUESTIONS].to_numpy()
    data["traitBased"] = np.average(traitScores, axis=1, weights=TRAIT_WEIGHTS)


def computeNegativeExceptional(data):
    """Changes all 4s in negative exceptional questions to 1,
    and the rest to 0
    :param data:
    :return:
    """
    mask = data[NEGATIVE_EXCEPTIONAL_QUESTIONS] == 4
    data.loc[:, NEGATIVE_EXCEPTIONAL_QUESTIONS] = mask.astype(int)


def computePositiveExceptional(data):
    """Changes all 4s in positive exceptional questions to 1,
    and the rest to 0
    :param data:
    :return:
    """
    mask = data[POSITIVE_EXCEPTIONAL_QUESTIONS] == 4
    data.loc[:, POSITIVE_EXCEPTIONAL_QUESTIONS] = mask.astype(int)


def computeExceptionalBased(data):
    """Subtracts sum of negative questions from sum of positive
    questions and divides by number of questions of each type
    :param data:
    :return:
    """
    sumPositive = data[POSITIVE_EXCEPTIONAL_QUESTIONS].to_numpy().sum(axis=1)
    sumNegative = data[NEGATIVE_EXCEPTIONAL_QUESTIONS].to_numpy().sum(axis=1)
    data["exceptionalBased"] = (
        sumPositive / POSITIVE_EXCEPTIONAL_QUESTION_COUNT
        - sumNegative / NEGATIVE_EXCEPTIONAL_QUESTION_COUNT
    )


def computeAppraiserImpression(data):
    """Computes appraiser impression based on the overall appraiser
    impression A00
    :param data:
    :return:
    """
    data["appraiserScore"] = data[APPRAISER_IMPRESSION_OVERALL_QUESTION]


def computeOQScore(data):
    """Computes the 'opScore' objective questions score based on
    'trait' and 'exceptional' based scores
    :param data:
    :return:
    """
    data["oqScore"] = data["traitBased"] + data["exceptionalBased"]


def computeAppraiserZscore(data):
    """Computes the Z score of appraiserScore
    :param data:
    :return:
    """
    # Uncomment the following to experiment
    ## Z Values
    # print(np.array([-3,-2,-1,0,1,2,3]))
    ## Probabilities
    # print(norm.cdf(np.array([-3,-2,-1,0,1,2,3])))
    ## Inverse Probability to Z Value
    # print(norm.ppf(norm.cdf(np.array([-3,-2,-1,0,1,2,3]))))
    data["appraiserScore_Zscore"] = (
        data["appraiserScore"] - data["appraiserScore"].mean()
    ) / data["appraiserScore"].std()


def computeOQZscore(data):
    """Computes the z score of objective questions based score
    :param data:
    :return:
    """
    data["oqScore_Zscore"] = (data["oqScore"] - data["oqScore"].mean()) / data[
        "oqScore"
    ].std()


def computeOverallZscore(data):
    """Computes the overall z score combining appraiser and
    oqScore and apply the specified weights"""
    data["overall_Zscore"] = (
        APPRAISER_IMPRESSION_WEIGHT * data["appraiserScore_Zscore"]
        + OQ_QUESTION_WEIGHT * data["oqScore_Zscore"]
    )


def computePvalue(data):
    """Computes the P value that is the area under the
    normal distribution curve from the left end
    :param data:
    :return:
    """
    data["overall_Pvalue"] = norm.cdf(data["overall_Zscore"])


def mapResponse(x):
    return {
        "evaluation_id": x["evaluation_id"],
        "traitBased": x["traitBased"],
        "exceptionalBased": x["exceptionalBased"],
        "appraiserScore": x["appraiserScore"],
        "oqScore": x["oqScore"],
        "appraiserScore_Zscore": x["appraiserScore_Zscore"],
        "oqScore_Zscore": x["oqScore_Zscore"],
        "overall_Zscore": x["overall_Zscore"],
        "overall_Pvalue": x["overall_Pvalue"],
    }


def process(input_args):
    """Processes the evaluation data to compute the P value
    :param inputfile:
    :param outputfile:
    :return:
    """
    print("input args", input_args)
    # data = pd.read_csv('testData.csv')
    data = pd.DataFrame.from_dict(input_args)
    print("data", data)
    # print('data1 from json',data1)
    computeTraitBased(data)
    computeNegativeExceptional(data)
    computePositiveExceptional(data)
    computeExceptionalBased(data)
    computeAppraiserImpression(data)
    computeOQScore(data)
    computeAppraiserZscore(data)
    computeOQZscore(data)
    computeOverallZscore(data)
    computePvalue(data)
    to_dict = data.to_dict("index")
    list_result = list(to_dict.values())
    final_response = list(map(mapResponse, list_result))
    return final_response


def lambda_handler(event, context):
    print("Received event: " + str(event))
    rawBody = event.get("body", None)
    if not rawBody:
        return {
            "statusCode": 200,
            "body": json.dumps({"message": "No body provided."}),
        }
    try:
        content = json.loads(rawBody)
        result = process(content)
        return {
            "statusCode": 200,
            "body": json.dumps(list(result)),
        }
    except:
        return {
            "statusCode": 500,
            "body": json.dumps({"message": "Unknown error occurred."}),
        }
