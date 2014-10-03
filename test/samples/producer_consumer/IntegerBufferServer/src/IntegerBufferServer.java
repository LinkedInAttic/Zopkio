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
import java.util.LinkedList;

public class IntegerBufferServer {
  private static final Logger logger = LogManager.getLogger(IntegerBufferServer.class.getCanonicalName());
  private static final Logger perfLogger = LogManager.getLogger("perf." + IntegerBufferServer.class.getCanonicalName());

  private static class FixedSizeBuffer {
    private LinkedList<Integer> buffer;
    private int capacity;
    private int size;

    public FixedSizeBuffer(int capacity) {
      this.buffer = new LinkedList<Integer>();
      this.capacity = capacity;
      this.size = 0;
    }

    public synchronized boolean put(Integer i) {
      if (size >= capacity) {
        return false;
      }

      buffer.add(i);
      size++;
      return true;
    }

    public synchronized Integer take() {
      if (size <= 0) {
        return null;
      }

      size--;
      return buffer.remove();
    }
  }

  private static class IntegerHandler implements HttpHandler {
    private static final int HTTP_OK = 200;
    private static final int HTTP_UNAVAILABLE = 503;

    private static void put(HttpExchange httpExchange) throws IOException {
      logger.info("Entering put request method...");
      BufferedReader bufferedReader = new BufferedReader(new InputStreamReader(httpExchange.getRequestBody()));
      String body = bufferedReader.readLine();
      bufferedReader.close();
      int num = Integer.parseInt(body);
      if (fixedSizeBuffer.put(num)) {
        httpExchange.sendResponseHeaders(HTTP_OK, 0);
        logger.trace("Received: " + body);
      }
      else {
        httpExchange.sendResponseHeaders(HTTP_UNAVAILABLE, 0);
        logger.trace("Full queue");
      }
      logger.info("Exiting put request method...");
    }

    private static void take(HttpExchange httpExchange) throws IOException {
      logger.info("Entering take command method...");
      Integer i = fixedSizeBuffer.take();
      if (i == null) {
        httpExchange.sendResponseHeaders(HTTP_UNAVAILABLE, 0);
        logger.trace("Empty queue");
      }
      else {
        String response = i.toString();
        httpExchange.sendResponseHeaders(HTTP_OK, response.length());
        OutputStream responseBody = httpExchange.getResponseBody();
        responseBody.write(response.getBytes());
        responseBody.flush();
        responseBody.close();
        logger.trace("Sent: " + response);
      }
      logger.info("Exiting take request method...");
    }

    public void handle(HttpExchange httpExchange) throws IOException {
      logger.info("[ENTER] http request handler...");
      long startTime = System.nanoTime();

      String requestMethod = httpExchange.getRequestMethod();
      if (requestMethod.equalsIgnoreCase("POST")) {
        put(httpExchange);
      }
      else if (requestMethod.equalsIgnoreCase("GET")) {
        take(httpExchange);
      }
      else {
        httpExchange.sendResponseHeaders(HTTP_OK, 0);
      }

      float executionTime = (float)(System.nanoTime() - startTime) / 1000000;
      perfLogger.info(String.format("%.3f", executionTime));
      logger.info("[EXIT] http request handler...");
    }
  }

  private static FixedSizeBuffer fixedSizeBuffer;

  public static void main(String[] args) throws IOException {
    fixedSizeBuffer = new FixedSizeBuffer(Integer.parseInt(args[2]));

    InetSocketAddress socketAddress = new InetSocketAddress(args[0], Integer.parseInt(args[1]));
    HttpServer httpServer = HttpServer.create(socketAddress, 0);
    httpServer.createContext("/", new IntegerHandler());
    httpServer.setExecutor(null);
    httpServer.start();
  }
}
