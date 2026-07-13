#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "AtlasVisualBridgeComponent.generated.h"

DECLARE_DYNAMIC_MULTICAST_DELEGATE_ThreeParams(FAtlasVisualEvent, FString, EventName, FString, Persona, FString, State);

UCLASS(ClassGroup=(ATLAS), meta=(BlueprintSpawnableComponent))
class ATLASCHAMBER_API UAtlasVisualBridgeComponent : public UActorComponent
{
    GENERATED_BODY()

public:
    UAtlasVisualBridgeComponent();

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="ATLAS")
    FString VisualSocketUrl = TEXT("ws://127.0.0.1:8000/api/atlas/visual/ws");

    UPROPERTY(BlueprintAssignable, Category="ATLAS")
    FAtlasVisualEvent OnAtlasVisualEvent;

    UFUNCTION(BlueprintCallable, Category="ATLAS")
    void Connect();

    UFUNCTION(BlueprintCallable, Category="ATLAS")
    void Disconnect();

protected:
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

private:
    TSharedPtr<class IWebSocket> Socket;
    void HandleMessage(const FString& Message);
};
