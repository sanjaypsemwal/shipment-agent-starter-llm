package com.example.agentclient;

import jakarta.validation.constraints.NotBlank;
import org.springframework.http.MediaType;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/orders")
public class OrderController {
    private final AgentClient agent;

    public OrderController(AgentClient agent) {
        this.agent = agent;
    }

    @GetMapping(value = "/{orderId}/ask", produces = MediaType.APPLICATION_JSON_VALUE)
    public String ask(@PathVariable("orderId") @NotBlank String orderId, @RequestParam("q") @NotBlank String question) {
        String goal = question + " (Order: " + orderId + ")";
        return agent.askAgent(goal);
    }
}
