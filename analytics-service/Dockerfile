# Runtime base image for .NET 9
FROM mcr.microsoft.com/dotnet/aspnet:9.0 AS base
WORKDIR /app
EXPOSE 8088

# SDK image for .NET 9 to build the app
FROM mcr.microsoft.com/dotnet/sdk:9.0 AS build
WORKDIR /src

# Copy project file and restore dependencies
COPY TodoAnalytics/*.csproj ./TodoAnalytics/
RUN dotnet restore ./TodoAnalytics/*.csproj

# Copy the full source code
COPY TodoAnalytics/. ./TodoAnalytics/

# Build the app
WORKDIR /src/TodoAnalytics
RUN dotnet build TodoAnalytics.csproj -c Release -o /app/build

# Publish the app
FROM build AS publish
RUN dotnet publish TodoAnalytics.csproj -c Release -o /app/publish /p:UseAppHost=false

# Final runtime image
FROM base AS final
WORKDIR /app
COPY --from=publish /app/publish .
ENTRYPOINT ["dotnet", "TodoAnalytics.dll"]
