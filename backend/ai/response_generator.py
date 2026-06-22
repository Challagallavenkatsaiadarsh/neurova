class ResponseGenerator:
    def generate(self, facts, style="grok"):
        if style == "grok":
            # This prompt tells the AI to sound like a witty, intelligent insider
            prompt = (
                f"You are an AI assistant with a witty, bold, and slightly edgy personality (think Grok). "
                f"Synthesize the following facts into a punchy, informative, and engaging response. "
                f"Do not use generic AI fillers like 'Here is the information'. "
                f"Facts: {facts}"
            )
            # CALL YOUR LLM HERE:
            # response = llm.generate_text(prompt)
            # return response
            
            # Temporary "Grok-style" mock formatting until you connect an LLM:
            return f"🔥 The reality check: {facts.strip()}. Pretty interesting, right?"
        
        return f"Fact update: {facts}"
