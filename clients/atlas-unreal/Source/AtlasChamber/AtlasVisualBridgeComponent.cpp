#include "AtlasVisualBridgeComponent.h"

#include "IWebSocket.h"
#include "Json.h"
#include "WebSocketsModule.h"

UAtlasVisualBridgeComponent::UAtlasVisualBridgeComponent()
{
    PrimaryComponentTick.bCanEverTick = false;
}

void UAtlasVisualBridgeComponent::Connect()
{
    if (Socket.IsValid() && Socket->IsConnected())
    {
        return;
    }

    if (!FModuleManager::Get().IsModuleLoaded("WebSockets"))
    {
        FModuleManager::Get().LoadModule("WebSockets");
    }

    Socket = FWebSocketsModule::Get().CreateWebSocket(VisualSocketUrl);
    Socket->OnMessage().AddUObject(this, &UAtlasVisualBridgeComponent::HandleMessage);
    Socket->Connect();
}

void UAtlasVisualBridgeComponent::Disconnect()
{
    if (Socket.IsValid())
    {
        Socket->Close();
        Socket.Reset();
    }
}

void UAtlasVisualBridgeComponent::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    Disconnect();
    Super::EndPlay(EndPlayReason);
}

void UAtlasVisualBridgeComponent::HandleMessage(const FString& Message)
{
    TSharedPtr<FJsonObject> Root;
    const TSharedRef<TJsonReader<>> Reader = TJsonReaderFactory<>::Create(Message);
    if (!FJsonSerializer::Deserialize(Reader, Root) || !Root.IsValid())
    {
        return;
    }

    FString EventName = Root->GetStringField(TEXT("event"));
    FString Persona = TEXT("atlas");
    FString State = TEXT("idle");

    const TSharedPtr<FJsonObject>* Payload = nullptr;
    if (Root->TryGetObjectField(TEXT("payload"), Payload) && Payload && Payload->IsValid())
    {
        (*Payload)->TryGetStringField(TEXT("persona"), Persona);
        (*Payload)->TryGetStringField(TEXT("state"), State);
    }

    OnAtlasVisualEvent.Broadcast(EventName, Persona, State);
}
