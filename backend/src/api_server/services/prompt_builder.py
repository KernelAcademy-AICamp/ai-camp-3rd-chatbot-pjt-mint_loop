"""Prompt building service for image generation."""
from ..config.constants import CONCEPT_VIBES, FILM_RENDERING
from ..models.requests import GenerateRequest


class PromptBuilder:
    """Service for building image generation prompts."""

    def build(self, request: GenerateRequest, translated: dict[str, str] | None = None) -> str:
        """Build prompt from request and translated fields."""
        t = translated or {}

        location = t.get('destination', request.destination)
        concept_vibe = CONCEPT_VIBES.get(request.concept, "atmospheric travel moment")
        film_style = FILM_RENDERING.get(request.filmType, request.filmStyleDescription)
        if not film_style:
            film_style = f"shot on {request.filmStock} film with characteristic analog tones"

        outfit = t.get('outfitStyle', request.outfitStyle) or "stylish travel outfit"

        # Extract chat context values
        city = t.get('city', '')
        spot_name = t.get('spotName', '')
        main_action = t.get('mainAction', '')
        chat_outfit = t.get('chatOutfitStyle', '')
        pose_detail = t.get('posePreference', '')
        film_type = ""
        camera_model = ""

        ctx = request.chatContext
        if ctx:
            city = city or ctx.city or ""
            spot_name = spot_name or ctx.spotName or ""
            main_action = main_action or ctx.mainAction or ""
            chat_outfit = chat_outfit or ctx.outfitStyle or ""
            pose_detail = pose_detail or ctx.posePreference or ""
            film_type = ctx.filmType or ""
            camera_model = ctx.cameraModel or ""

        final_outfit = chat_outfit or outfit

        # Build scene description
        user_scene = t.get('additionalPrompt', request.additionalPrompt.strip() if request.additionalPrompt else "")
        scene_description = self._build_scene(main_action, user_scene)

        # Build prompt based on available context
        if ctx and (main_action or spot_name or pose_detail):
            prompt = self._build_detailed_prompt(
                location, spot_name, scene_description, final_outfit,
                pose_detail, film_type or request.filmStock, film_style,
                camera_model, concept_vibe, request.filmStock
            )
        else:
            prompt = self._build_simple_prompt(location, final_outfit, film_style, concept_vibe)

        if request.conversationSummary:
            prompt += f"\n\nAdditional notes from conversation:\n{request.conversationSummary}"

        return prompt

    def _build_scene(self, action: str, user_scene: str) -> str:
        """Combine action and user scene description."""
        if user_scene and action and user_scene != action:
            return f"{action}. {user_scene}"
        return action or user_scene or ""

    def _build_detailed_prompt(
        self, location: str, spot_name: str, scene: str, outfit: str,
        pose: str, film: str, film_style: str, camera: str, vibe: str, film_stock: str
    ) -> str:
        """Build detailed prompt with full context."""
        loc = f"{location}, specifically at {spot_name}" if spot_name and spot_name.lower() not in location.lower() else location
        camera_line = f"Shot with {camera}, capturing its characteristic rendering" if camera else "Classic analog film camera aesthetic"
        scene_text = scene or "enjoying a peaceful moment of travel"
        pose_text = pose or "in a natural, candid pose"

        return f"""A highly detailed cinematic travel photograph.

                A person at {loc}, {scene_text}.

                The person is wearing {outfit}, {pose_text}. Their expression shows authentic, genuine emotion. Realistic body proportions and natural positioning.

                Photography style: {film} film with {film_style}. {camera_line}. The mood is {vibe}.

                Technical details: Cinematic rule of thirds composition. Golden hour or soft natural light. Shallow depth of field with gentle bokeh. Authentic film grain of {film_stock}. Warm, nostalgic color tones."""

    def _build_simple_prompt(self, location: str, outfit: str, film_style: str, vibe: str) -> str:
        """Build simple prompt without detailed context."""
        return f"""A cinematic travel photograph at {location}.

                A traveler enjoying a quiet moment, captured candidly. Wearing {outfit}, in a relaxed pose with authentic expression.

                Visual style: {film_style}. {vibe}. Soft film grain with warm nostalgic tones. Shallow depth of field. Beautiful natural lighting. Cinematic framing."""
