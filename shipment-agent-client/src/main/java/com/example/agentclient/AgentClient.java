package com.example.agentclient;
import org.springframework.http.*; import org.springframework.stereotype.Component; import org.springframework.web.client.RestClient;
@Component
public class AgentClient { private final RestClient rest = RestClient.create("http://localhost:8000"); public String askAgent(String goal){ var body="{\"goal\":\""+goal.replace("\"","'")+"\",\"max_steps\":3}"; var resp=rest.post().uri("/agent/run").contentType(MediaType.APPLICATION_JSON).body(body).retrieve().toEntity(String.class); return resp.getBody(); }}
