package com.example.demo;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.Map;

@RestController
public class DemoController {

    @GetMapping("/health")
    public Map<String, Object> health() {
        return Map.of(
                "status", "UP",
                "application", "demo-app"
        );
    }

    @GetMapping("/api/test")
    public Map<String, Object> test() {
        return Map.of(
                "message", "compatibility-test-ok",
                "application", "demo-app"
        );
    }
}
