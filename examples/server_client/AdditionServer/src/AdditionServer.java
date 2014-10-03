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

import com.sun.net.httpserver.HttpExchange;
import com.sun.net.httpserver.HttpHandler;
import com.sun.net.httpserver.HttpServer;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.net.InetSocketAddress;

public class AdditionServer {
  private static final Logger logger = LogManager.getLogger(AdditionServer.class.getCanonicalName());
  private static final Logger perfLogger = LogManager.getLogger("perf." + AdditionServer.class.getCanonicalName());

  private static final int MAX_BACKLOG = 0;
  private static final int HTTP_OK = 200;

  public static void main(String[] args) {
    InetSocketAddress socketAddress = new InetSocketAddress(args[0], Integer.parseInt(args[1]));
    try {
      HttpServer httpServer = HttpServer.create(socketAddress, MAX_BACKLOG);
      httpServer.createContext("/", new AdditionHandler());
      httpServer.setExecutor(null);
      httpServer.start();
      logger.info("Starting addition server.");
    }
    catch (IOException ioe) {
      logger.error("Could not start addition server. Exiting...", ioe);
      return;
    }
  }

  static class AdditionHandler implements HttpHandler {
    private static int sum = 0;

    private static boolean isInt(String str) {
      try {
        Integer.parseInt(str);
      }
      catch (NumberFormatException nfe) {
        return false;
      }
      return true;
    }

    public void handle(HttpExchange httpExchange) throws IOException {
      logger.info("[ENTER] http request handler...");
      long startTime = System.nanoTime();

      String requestMethod = httpExchange.getRequestMethod();
      logger.info("Received a " + requestMethod + " request");
      if (requestMethod.equalsIgnoreCase("POST")) {
        BufferedReader bufferedReader = new BufferedReader(new InputStreamReader(httpExchange.getRequestBody()));
        String body = bufferedReader.readLine();
        logger.info("Received " + body);
        if (isInt(body)) {
          int num = Integer.parseInt(body);
          sum += num;
        }
        logger.info("Sum is now " + sum);
        bufferedReader.close();
        httpExchange.sendResponseHeaders(HTTP_OK, 0);
      }
      else if (requestMethod.equalsIgnoreCase("GET")) {
        String response = Integer.toString(sum);
        httpExchange.sendResponseHeaders(HTTP_OK, response.length());
        OutputStream responseBody = httpExchange.getResponseBody();
        responseBody.write(response.getBytes());
        responseBody.flush();
        responseBody.close();
        logger.info("Responding with " + sum);

        sum = 0;
      }
      else {
        // a response must be sent or else the client will hang
        httpExchange.sendResponseHeaders(HTTP_OK, 0);
      }

      float executionTime = (float)(System.nanoTime() - startTime) / 1000000;
      perfLogger.info(String.format("%.3f", executionTime));
      logger.info("[EXIT] http request handler...");
    }
  }
}
