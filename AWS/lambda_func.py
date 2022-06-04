import json
import traceback
import logging
import sys
import os
from time import time

import base64
import time

def dict_from_payload(base64_input: str):
    """ Decodes a base64-encoded binary payload into JSON.
            Parameters 
            ----------
            base64_input : str
                Base64-encoded binary payload
                
            Returns
            -------
            JSON object with key/value pairs of decoded attributes

        """
    #bytes = base64.b64decode(base64_input).hex()
    
    decoded = base64.b64decode(base64_input)

    byteArray = list(decoded)
    
    temp = (byteArray[0] << 8 | byteArray[1] ) / 100
    rel_hum =  (byteArray[2] << 8 | byteArray[3] )
    pm25_standard = (byteArray[4] << 8 | byteArray[5] ) 
    pm100_standard =  (byteArray[6] << 8 | byteArray[7] ) 
    uv = (byteArray[8] << 8 | byteArray[9] ) / 100
    ir =  (byteArray[10] << 8 | byteArray[11] )
    view = (byteArray[12] << 8 | byteArray[13] ) 
    volt =  (byteArray[14] << 8 | byteArray[15] ) / 1000
    timestamp =  (byteArray[16] << 24 | byteArray[17] << 16 | byteArray[18] << 8 | byteArray[19] ) 
            
    result = {
        "temperature": temp,
        "humidity": rel_hum,
        "pm2.5": pm25_standard,
        "pm10": pm100_standard,
        "ultraviolet": uv,
        "infrared": ir,
        "visible": view,
        "voltage": volt,
        "timestamp": timestamp
    }

    return result


# Setup  logging
logger = logging.getLogger("PayloadDecoder")
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    """ Transforms a binary payload by invoking "decode_{event.type}" function
        Parameters
        ----------
        DeviceId : str
            Device Id
        ApplicationId : int
            LoRaWAN Application Id / Port number
        PayloadData : str
            Base64 encoded input payload

        Returns
        -------
        This function returns a JSON object with the following keys:

        - status: 200 or 500
        - transformed_payload: result of calling ".dict_from_payload"      (only if status == 200)
        - lns_payload: a representation of payload as received from an LNS
        - error_type                                                        (only if status == 500)
        - error_message                                                     (only if status == 500)
        - stackTrace                                                        (only if status == 500)
    """

    logger.info("Received event: %s" % json.dumps(event))

    try:

        # Invoke a payload conversion function
        decoded_payload = dict_from_payload(event.get("PayloadData"))

        # Define the output of AWS Lambda function in case of successful decoding
        result = {
            "status": 200,
            "LNSData": {
                "PayloadData": event.get("PayloadData"),
                "WirelessDeviceId": event.get("WirelessDeviceId"),
                "WirelessMetadata": {"LoRaWAN": event.get("WirelessMetadata")["LoRaWAN"]}
            },
            "TransformedPayloadData": decoded_payload
        }
        logger.info(result)
        return result

    except Exception as exp:

        exception_type, exception_value, exception_traceback = sys.exc_info()
        traceback_string = traceback.format_exception(
            exception_type, exception_value, exception_traceback)

        # Define the output of AWS Lambda function in case of error

        exception_error_message = {
            "errorType": exception_type.__name__,
            "errorMessage": str(exception_value),
            "stackTrace": traceback_string
        }

        logger.error("Exception during execution, details : %s " %
                     json.dumps(exception_error_message))

        # Finish AWS lambda processing with an error
        raise exp

