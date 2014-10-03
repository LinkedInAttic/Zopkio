/*
 * Licensed to the Apache Software Foundation (ASF) under one
 * or more contributor license agreements.  See the NOTICE file
 * distributed with this work for additional information
 * regarding copyright ownership.  The ASF licenses this file
 * to you under the Apache License, Version 2.0 (the
 * "License"); you may not use this file except in compliance
 * with the License.  You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing,
 * software distributed under the License is distributed on an
 * "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
 * KIND, either express or implied.  See the License for the
 * specific language governing permissions and limitations
 * under the License.
 */

import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.OutputStreamWriter;
import java.net.HttpURLConnection;
import java.net.SocketTimeoutException;
import java.net.URL;

public class AdditionClient {
  private static final Logger logger = LogManager.getLogger(AdditionClient.class.getCanonicalName());
  private static final Logger perfLogger = LogManager.getLogger("perf." + AdditionClient.class.getCanonicalName());

  private static final int TIMEOUT = 0;
  private static final int HTTP_OK = 200;

  private static HttpURLConnection getUrlConnection(String strUrl, String requestMethod) throws IOException {
    logger.info("[ENTER] getUrlConnection with " + requestMethod);
    URL url = new URL(strUrl);
    HttpURLConnection urlConnection = (HttpURLConnection) url.openConnection();
    urlConnection.setConnectTimeout(TIMEOUT);
    urlConnection.setReadTimeout(TIMEOUT);
    urlConnection.setDoOutput(true);
    urlConnection.setRequestMethod(requestMethod);

    logger.info("[EXIT] returning urlConnection");
    return urlConnection;
  }

  public static void main(String[] args) throws IOException {
    long startTime = System.nanoTime();

    String strUrl = "http://" + args[0] + ":" + args[1];
    try {
      for (int i = 2; i < args.length; ++i) {
        HttpURLConnection urlConnection = getUrlConnection(strUrl, "POST");
        OutputStreamWriter out = new OutputStreamWriter(urlConnection.getOutputStream());
        String str = args[i];
        logger.info("Attempting to send " + str);
        out.write(str);
        out.flush();
        out.close();

        // http request is actually sent when the input stream is opened
        BufferedReader response = new BufferedReader(new InputStreamReader(urlConnection.getInputStream()));
        response.close();
        logger.info("Sent: " + str);
      }

      HttpURLConnection urlConnection = getUrlConnection(strUrl, "GET");
      BufferedReader response = new BufferedReader(new InputStreamReader(urlConnection.getInputStream()));
      if (response.ready()) {
        if (urlConnection.getResponseCode() != HTTP_OK) {
          logger.error("Could not retrieve sum");
          return;
        }
        logger.info("Received: " + response.readLine());
      }
      response.close();
    }
    catch (SocketTimeoutException ste) {
      logger.error("Server timeout", ste);
      return;
    }
    catch (IOException ioe) {
      logger.error("Addition failed", ioe);
      return;
    }

    float executionTime = (float)(System.nanoTime() - startTime) / 1000000;
    perfLogger.info(String.format("%.3f", executionTime));
  }
}
